package com.logistics.hub;

import com.logistics.hub.dto.OrderDtos;
import com.logistics.hub.entity.Order;
import com.logistics.hub.entity.Product;
import com.logistics.hub.entity.Shipment;
import com.logistics.hub.entity.User;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.OrderRepository;
import com.logistics.hub.repository.ProductRepository;
import com.logistics.hub.repository.ShipmentRepository;
import com.logistics.hub.repository.UserRepository;
import com.logistics.hub.service.OrderService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ProductRepository productRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private ShipmentRepository shipmentRepository;

    @InjectMocks
    private OrderService orderService;

    private User user;
    private Product product;
    private Order order;
    private OrderDtos.OrderRequest orderRequest;

    @BeforeEach
    void setUp() {
        user = User.builder()
                .id(1L)
                .username("john_doe")
                .email("john@example.com")
                .fullName("John Doe")
                .build();

        product = Product.builder()
                .id(1L)
                .sku("SKU-1")
                .name("Wireless Mouse")
                .price(BigDecimal.valueOf(25.00))
                .stockQuantity(10)
                .weightGrams(200)
                .isActive(true)
                .build();

        order = Order.builder()
                .id(1L)
                .orderNumber("ORD-12345")
                .customer(user)
                .status(Order.OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(25.00))
                .shippingAddress("123 Street")
                .build();

        OrderDtos.OrderItemRequest itemRequest = new OrderDtos.OrderItemRequest();
        itemRequest.setProductId(1L);
        itemRequest.setQuantity(2);

        orderRequest = new OrderDtos.OrderRequest();
        orderRequest.setShippingAddress("123 Street");
        orderRequest.setNotes("Leave at door");
        orderRequest.setItems(Collections.singletonList(itemRequest));
    }

    @Test
    void getAllOrders_success() {
        PageRequest pageable = PageRequest.of(0, 10, Sort.by("createdAt").descending());
        Page<Order> page = new PageImpl<>(Collections.singletonList(order), pageable, 1);
        when(orderRepository.findAll(pageable)).thenReturn(page);

        Page<OrderDtos.OrderResponse> response = orderService.getAllOrders(0, 10);

        assertThat(response).isNotNull();
        assertThat(response.getContent()).hasSize(1);
        assertThat(response.getContent().get(0).getOrderNumber()).isEqualTo("ORD-12345");
    }

    @Test
    void getOrdersByCustomer_success() {
        PageRequest pageable = PageRequest.of(0, 10, Sort.by("createdAt").descending());
        Page<Order> page = new PageImpl<>(Collections.singletonList(order), pageable, 1);
        when(orderRepository.findByCustomerId(1L, pageable)).thenReturn(page);

        Page<OrderDtos.OrderResponse> response = orderService.getOrdersByCustomer(1L, 0, 10);

        assertThat(response).isNotNull();
        assertThat(response.getContent()).hasSize(1);
    }

    @Test
    void getOrdersByUsername_success() {
        PageRequest pageable = PageRequest.of(0, 10, Sort.by("createdAt").descending());
        Page<Order> page = new PageImpl<>(Collections.singletonList(order), pageable, 1);
        when(userRepository.findByUsername("john_doe")).thenReturn(Optional.of(user));
        when(orderRepository.findByCustomerId(1L, pageable)).thenReturn(page);

        Page<OrderDtos.OrderResponse> response = orderService.getOrdersByUsername("john_doe", 0, 10);

        assertThat(response).isNotNull();
        assertThat(response.getContent()).hasSize(1);
    }

    @Test
    void getOrdersByUsername_notFound_throwsException() {
        when(userRepository.findByUsername("unknown")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.getOrdersByUsername("unknown", 0, 10))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    void getOrderById_success() {
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        OrderDtos.OrderResponse response = orderService.getOrderById(1L);

        assertThat(response).isNotNull();
        assertThat(response.getId()).isEqualTo(1L);
    }

    @Test
    void getOrderById_notFound_throwsException() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.getOrderById(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    void createOrder_success() {
        when(userRepository.findByUsername("john_doe")).thenReturn(Optional.of(user));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(orderRepository.save(any(Order.class))).thenReturn(order);
        when(shipmentRepository.save(any(Shipment.class))).thenReturn(new Shipment());

        OrderDtos.OrderResponse response = orderService.createOrder(orderRequest, "john_doe");

        assertThat(response).isNotNull();
        assertThat(product.getStockQuantity()).isEqualTo(8); // 10 - 2
        verify(productRepository).save(product);
        verify(orderRepository).save(any(Order.class));
        verify(shipmentRepository).save(any(Shipment.class));
    }

    @Test
    void createOrder_insufficientStock_throwsException() {
        product.setStockQuantity(1); // request quantity is 2
        when(userRepository.findByUsername("john_doe")).thenReturn(Optional.of(user));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        assertThatThrownBy(() -> orderService.createOrder(orderRequest, "john_doe"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Insufficient stock");

        verify(productRepository, never()).save(any(Product.class));
        verify(orderRepository, never()).save(any(Order.class));
    }

    @Test
    void updateOrderStatus_success() {
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));
        when(orderRepository.save(any(Order.class))).thenReturn(order);

        OrderDtos.OrderResponse response = orderService.updateOrderStatus(1L, Order.OrderStatus.SHIPPED);

        assertThat(response).isNotNull();
        assertThat(order.getStatus()).isEqualTo(Order.OrderStatus.SHIPPED);
    }
}
