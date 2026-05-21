package com.logistics.hub.service;

import com.logistics.hub.dto.OrderDtos;
import com.logistics.hub.entity.Shipment;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.ShipmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ShipmentService {

    private final ShipmentRepository shipmentRepository;

    private OrderDtos.ShipmentResponse toResponse(Shipment s) {
        OrderDtos.ShipmentResponse r = new OrderDtos.ShipmentResponse();
        r.setId(s.getId());
        r.setTrackingNumber(s.getTrackingNumber());
        r.setOrderNumber(s.getOrder() != null ? s.getOrder().getOrderNumber() : null);
        r.setMode(s.getMode().name());
        r.setStatus(s.getStatus().name());
        r.setCarrier(s.getCarrier());
        r.setWeightGrams(s.getWeightGrams());
        r.setCustomerCareCalls(s.getCustomerCareCalls());
        r.setCustomerRating(s.getCustomerRating());
        r.setDiscountOffered(s.getDiscountOffered());
        r.setDeliveredOnTime(s.getDeliveredOnTime());
        r.setEstimatedDelivery(s.getEstimatedDelivery());
        r.setActualDelivery(s.getActualDelivery());
        r.setCreatedAt(s.getCreatedAt());
        return r;
    }

    public Page<OrderDtos.ShipmentResponse> getAllShipments(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return shipmentRepository.findAll(pageable).map(this::toResponse);
    }

    public OrderDtos.ShipmentResponse getByTrackingNumber(String trackingNumber) {
        Shipment shipment = shipmentRepository.findByTrackingNumber(trackingNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Shipment", "trackingNumber", trackingNumber));
        return toResponse(shipment);
    }

    @Transactional
    public OrderDtos.ShipmentResponse updateShipment(Long id, OrderDtos.ShipmentUpdateRequest request) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Shipment", "id", id));
        if (request.getStatus() != null) shipment.setStatus(request.getStatus());
        if (request.getCustomerRating() != null) shipment.setCustomerRating(request.getCustomerRating());
        if (request.getDeliveredOnTime() != null) shipment.setDeliveredOnTime(request.getDeliveredOnTime());
        if (request.getActualDelivery() != null) shipment.setActualDelivery(request.getActualDelivery());
        return toResponse(shipmentRepository.save(shipment));
    }

    @Transactional
    public OrderDtos.ShipmentResponse rateShipment(Long id, Integer rating) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Shipment", "id", id));
        shipment.setCustomerRating(rating);
        return toResponse(shipmentRepository.save(shipment));
    }

    public Double getOnTimeDeliveryRate() {
        Double rate = shipmentRepository.getOnTimeDeliveryRate();
        return rate != null ? Math.round(rate * 10000.0) / 100.0 : 0.0;
    }
}
