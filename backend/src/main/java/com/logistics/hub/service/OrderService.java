package com.logistics.hub.service;

import com.logistics.hub.dto.OrderDtos;
import com.logistics.hub.entity.*;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final UserRepository userRepository;
    private final ShipmentRepository shipmentRepository;

    private OrderDtos.OrderResponse toResponse(Order order) {
        OrderDtos.OrderResponse r = new OrderDtos.OrderResponse();
        r.setId(order.getId());
        r.setOrderNumber(order.getOrderNumber());
        r.setCustomerName(order.getCustomer() != null ? order.getCustomer().getFullName() : "N/A");
        r.setStatus(order.getStatus().name());
        r.setTotalAmount(order.getTotalAmount());
        r.setDiscountAmount(order.getDiscountAmount());
        r.setShippingAddress(order.getShippingAddress());
        r.setCreatedAt(order.getCreatedAt());

        if (order.getItems() != null) {
            r.setItems(order.getItems().stream().map(item -> {
                OrderDtos.OrderItemResponse ir = new OrderDtos.OrderItemResponse();
                ir.setProductId(item.getProduct().getId());
                ir.setProductName(item.getProduct().getName());
                ir.setQuantity(item.getQuantity());
                ir.setUnitPrice(item.getUnitPrice());
                ir.setSubtotal(item.getSubtotal());
                return ir;
            }).collect(Collectors.toList()));
        }

        if (order.getShipment() != null) {
            OrderDtos.ShipmentSummary ss = new OrderDtos.ShipmentSummary();
            ss.setId(order.getShipment().getId());
            ss.setTrackingNumber(order.getShipment().getTrackingNumber());
            ss.setStatus(order.getShipment().getStatus().name());
            ss.setEstimatedDelivery(order.getShipment().getEstimatedDelivery());
            ss.setCustomerRating(order.getShipment().getCustomerRating());
            r.setShipment(ss);
        }
        return r;
    }

    public Page<OrderDtos.OrderResponse> getAllOrders(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return orderRepository.findAll(pageable).map(this::toResponse);
    }

    public Page<OrderDtos.OrderResponse> getOrdersByCustomer(Long customerId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return orderRepository.findByCustomerId(customerId, pageable).map(this::toResponse);
    }

    public Page<OrderDtos.OrderResponse> getOrdersByUsername(String username, int page, int size) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User", "username", username));
        return getOrdersByCustomer(user.getId(), page, size);
    }

    public OrderDtos.OrderResponse getOrderById(Long id) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Order", "id", id));
        return toResponse(order);
    }

    @Transactional
    public OrderDtos.OrderResponse createOrder(OrderDtos.OrderRequest request, String username) {
        User customer = userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User", "username", username));

        List<OrderItem> items = request.getItems().stream().map(itemReq -> {
            Product product = productRepository.findById(itemReq.getProductId())
                .orElseThrow(() -> new ResourceNotFoundException("Product", "id", itemReq.getProductId()));
            if (product.getStockQuantity() < itemReq.getQuantity()) {
            throw new IllegalArgumentException("Insufficient stock for product: '" + product.getName() + "' (SKU: " + product.getSku() + "). Requested: " + itemReq.getQuantity() + ", Available: " + product.getStockQuantity());
            }

            BigDecimal subtotal = product.getPrice().multiply(BigDecimal.valueOf(itemReq.getQuantity()));
            product.setStockQuantity(product.getStockQuantity() - itemReq.getQuantity());
            productRepository.save(product);

            return OrderItem.builder()
                .product(product)
                .quantity(itemReq.getQuantity())
                .unitPrice(product.getPrice())
                .subtotal(subtotal)
                .build();
        }).collect(Collectors.toList());

        BigDecimal total = items.stream()
                .map(OrderItem::getSubtotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Order order = Order.builder()
                .orderNumber("ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .customer(customer)
                .status(Order.OrderStatus.PENDING)
                .totalAmount(total)
                .discountAmount(BigDecimal.ZERO)
                .shippingAddress(request.getShippingAddress())
                .notes(request.getNotes())
                .items(items)
                .build();

        items.forEach(item -> item.setOrder(order));
        Order savedOrder = orderRepository.save(order);

        // Calculate total shipment weight from ordered products
        int totalWeightGrams = items.stream()
                .mapToInt(item -> {
                    int w = item.getProduct().getWeightGrams() != null ? item.getProduct().getWeightGrams() : 0;
                    return w * item.getQuantity();
                }).sum();

        // Auto-create shipment
        Shipment shipment = Shipment.builder()
                .trackingNumber("TRK-" + UUID.randomUUID().toString().substring(0, 10).toUpperCase())
                .order(savedOrder)
                .mode(Shipment.ShipmentMode.Road)
                .status(Shipment.ShipmentStatus.PREPARING)
                .estimatedDelivery(LocalDate.now().plusDays(7))
                .weightGrams(Math.max(totalWeightGrams, 1))
                .discountOffered(BigDecimal.ZERO)
                .customerCareCalls(0)
                .customerRating(3)
                .deliveredOnTime(false)
                .build();
        shipmentRepository.save(shipment);

        return toResponse(savedOrder);
    }

    @Transactional
    public OrderDtos.OrderResponse updateOrderStatus(Long id, Order.OrderStatus status) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Order", "id", id));
        order.setStatus(status);
        return toResponse(orderRepository.save(order));
    }
}
