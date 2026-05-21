package com.logistics.hub.dto;

import com.logistics.hub.entity.Shipment;
import jakarta.validation.constraints.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public class OrderDtos {

    @Data
    public static class OrderItemRequest {
        @NotNull private Long productId;
        @NotNull @Min(1) private Integer quantity;
    }

    @Data
    public static class OrderRequest {
        @NotBlank private String shippingAddress;
        private String notes;
        @NotEmpty private List<OrderItemRequest> items;
    }

    @Data
    public static class OrderResponse {
        private Long id;
        private String orderNumber;
        private String customerName;
        private String status;
        private BigDecimal totalAmount;
        private BigDecimal discountAmount;
        private String shippingAddress;
        private List<OrderItemResponse> items;
        private ShipmentSummary shipment;
        private LocalDateTime createdAt;
    }

    @Data
    public static class OrderItemResponse {
        private Long productId;
        private String productName;
        private Integer quantity;
        private BigDecimal unitPrice;
        private BigDecimal subtotal;
    }

    @Data
    public static class ShipmentSummary {
        private Long id;
        private String trackingNumber;
        private String status;
        private LocalDate estimatedDelivery;
        private Integer customerRating;
    }

    @Data
    public static class ShipmentUpdateRequest {
        private Shipment.ShipmentStatus status;
        private Integer customerRating;
        private Boolean deliveredOnTime;
        private LocalDate actualDelivery;
    }

    @Data
    public static class ShipmentResponse {
        private Long id;
        private String trackingNumber;
        private String orderNumber;
        private String mode;
        private String status;
        private String carrier;
        private Integer weightGrams;
        private Integer customerCareCalls;
        private Integer customerRating;
        private BigDecimal discountOffered;
        private Boolean deliveredOnTime;
        private LocalDate estimatedDelivery;
        private LocalDate actualDelivery;
        private LocalDateTime createdAt;
    }
}
