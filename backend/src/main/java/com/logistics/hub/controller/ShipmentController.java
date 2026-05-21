package com.logistics.hub.controller;

import com.logistics.hub.dto.OrderDtos;
import com.logistics.hub.entity.Shipment;
import com.logistics.hub.service.ShipmentService;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/shipments")
@RequiredArgsConstructor
@Validated
public class ShipmentController {

    private final ShipmentService shipmentService;

    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Page<OrderDtos.ShipmentResponse>> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return ResponseEntity.ok(shipmentService.getAllShipments(page, size));
    }

    @GetMapping("/track/{trackingNumber}")
    public ResponseEntity<OrderDtos.ShipmentResponse> trackShipment(
            @PathVariable String trackingNumber) {
        return ResponseEntity.ok(shipmentService.getByTrackingNumber(trackingNumber));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<OrderDtos.ShipmentResponse> update(
            @PathVariable Long id,
            @RequestBody OrderDtos.ShipmentUpdateRequest request) {
        return ResponseEntity.ok(shipmentService.updateShipment(id, request));
    }

    // Admin-only shortcut: update just the shipment status
    @PutMapping("/{id}/status")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<OrderDtos.ShipmentResponse> updateStatus(
            @PathVariable Long id,
            @RequestParam Shipment.ShipmentStatus status) {
        OrderDtos.ShipmentUpdateRequest req = new OrderDtos.ShipmentUpdateRequest();
        req.setStatus(status);
        return ResponseEntity.ok(shipmentService.updateShipment(id, req));
    }

    // Customer rates their delivered shipment (1-5 stars)
    @PutMapping("/{id}/rate")
    public ResponseEntity<OrderDtos.ShipmentResponse> rate(
            @PathVariable Long id,
            @RequestParam @Min(1) @Max(5) Integer rating) {
        return ResponseEntity.ok(shipmentService.rateShipment(id, rating));
    }

    @GetMapping("/analytics/on-time-rate")
    public ResponseEntity<Double> getOnTimeRate() {
        return ResponseEntity.ok(shipmentService.getOnTimeDeliveryRate());
    }
}
