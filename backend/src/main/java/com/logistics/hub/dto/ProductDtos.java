package com.logistics.hub.dto;

import com.logistics.hub.entity.Product;
import jakarta.validation.constraints.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class ProductDtos {

    @Data
    public static class ProductRequest {
        @NotBlank @Size(max = 50)
        private String sku;

        @NotBlank @Size(max = 200)
        private String name;

        private String description;

        @NotNull
        private Long categoryId;

        @NotNull @DecimalMin("0.01")
        private BigDecimal cost;

        @NotNull @DecimalMin("0.01")
        private BigDecimal price;

        @Min(0) private Integer weightGrams = 0;

        private Product.Importance importance = Product.Importance.MEDIUM;

        @Min(0) private Integer stockQuantity = 0;

        private Long warehouseId;
    }

    @Data
    public static class ProductResponse {
        private Long id;
        private String sku;
        private String name;
        private String description;
        private String categoryName;
        private Long categoryId;
        private BigDecimal cost;
        private BigDecimal price;
        private Integer weightGrams;
        private String importance;
        private Integer stockQuantity;
        private String warehouseName;
        private boolean isActive;
        private LocalDateTime createdAt;
    }
}
