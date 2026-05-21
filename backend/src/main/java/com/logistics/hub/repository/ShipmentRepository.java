package com.logistics.hub.repository;

import com.logistics.hub.entity.Shipment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface ShipmentRepository extends JpaRepository<Shipment, Long> {
    Optional<Shipment> findByTrackingNumber(String trackingNumber);
    Optional<Shipment> findByOrderId(Long orderId);
    Page<Shipment> findByStatus(Shipment.ShipmentStatus status, Pageable pageable);

    @Query("SELECT s.mode, COUNT(s) FROM Shipment s GROUP BY s.mode")
    java.util.List<Object[]> countByMode();

    @Query("SELECT AVG(CASE WHEN s.deliveredOnTime = true THEN 1.0 ELSE 0.0 END) FROM Shipment s WHERE s.deliveredOnTime IS NOT NULL")
    Double getOnTimeDeliveryRate();
}
