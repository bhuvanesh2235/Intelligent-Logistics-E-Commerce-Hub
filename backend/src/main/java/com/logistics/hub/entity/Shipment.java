package com.logistics.hub.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "shipments")
@EntityListeners(AuditingEntityListener.class)
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Shipment {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "tracking_number", nullable = false, unique = true, length = 50)
    private String trackingNumber;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "warehouse_id")
    private Warehouse warehouse;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ShipmentMode mode = ShipmentMode.Road;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ShipmentStatus status = ShipmentStatus.PREPARING;

    @Column(length = 100)
    private String carrier;

    @Column(name = "weight_grams")
    private Integer weightGrams;

    @Builder.Default
    @Column(name = "customer_care_calls")
    private Integer customerCareCalls = 0;

    @Column(name = "customer_rating")
    private Integer customerRating;

    @Builder.Default
    @Column(name = "discount_offered", precision = 5, scale = 2)
    private BigDecimal discountOffered = BigDecimal.ZERO;

    @Column(name = "delivered_on_time")
    private Boolean deliveredOnTime;

    @Column(name = "estimated_delivery")
    private LocalDate estimatedDelivery;

    @Column(name = "actual_delivery")
    private LocalDate actualDelivery;

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public enum ShipmentMode { Ship, Flight, Road }
    public enum ShipmentStatus { PREPARING, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED }
}
