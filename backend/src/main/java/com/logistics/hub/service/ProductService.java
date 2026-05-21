package com.logistics.hub.service;

import com.logistics.hub.dto.ProductDtos;
import com.logistics.hub.entity.Category;
import com.logistics.hub.entity.Product;
import com.logistics.hub.entity.Warehouse;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    // ── Helpers ─────────────────────────────────────────────────────────────
    private ProductDtos.ProductResponse toResponse(Product p) {
        ProductDtos.ProductResponse r = new ProductDtos.ProductResponse();
        r.setId(p.getId());
        r.setSku(p.getSku());
        r.setName(p.getName());
        r.setDescription(p.getDescription());
        r.setCategoryId(p.getCategory() != null ? p.getCategory().getId() : null);
        r.setCategoryName(p.getCategory() != null ? p.getCategory().getName() : null);
        r.setCost(p.getCost());
        r.setPrice(p.getPrice());
        r.setWeightGrams(p.getWeightGrams());
        r.setImportance(p.getImportance().name());
        r.setStockQuantity(p.getStockQuantity());
        r.setWarehouseName(p.getWarehouse() != null ? p.getWarehouse().getName() : null);
        r.setActive(p.isActive());
        r.setCreatedAt(p.getCreatedAt());
        return r;
    }

    // ── CRUD ─────────────────────────────────────────────────────────────────
    public Page<ProductDtos.ProductResponse> getAllProducts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return productRepository.findByIsActiveTrue(pageable).map(this::toResponse);
    }

    public ProductDtos.ProductResponse getProductById(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Product", "id", id));
        return toResponse(product);
    }

    @Transactional
    public ProductDtos.ProductResponse createProduct(ProductDtos.ProductRequest request) {
        if (productRepository.existsBySku(request.getSku()))
            throw new IllegalArgumentException("SKU already exists: " + request.getSku());

        Category category = new Category();
        category.setId(request.getCategoryId());

        Product product = Product.builder()
                .sku(request.getSku())
                .name(request.getName())
                .description(request.getDescription())
                .category(category)
                .cost(request.getCost())
                .price(request.getPrice())
                .weightGrams(request.getWeightGrams())
                .importance(request.getImportance())
                .stockQuantity(request.getStockQuantity())
                .isActive(true)
                .build();

        if (request.getWarehouseId() != null) {
            Warehouse wh = new Warehouse();
            wh.setId(request.getWarehouseId());
            product.setWarehouse(wh);
        }

        return toResponse(productRepository.save(product));
    }

    @Transactional
    public ProductDtos.ProductResponse updateProduct(Long id, ProductDtos.ProductRequest request) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Product", "id", id));

        product.setName(request.getName());
        product.setDescription(request.getDescription());
        product.setCost(request.getCost());
        product.setPrice(request.getPrice());
        product.setWeightGrams(request.getWeightGrams());
        product.setImportance(request.getImportance());
        product.setStockQuantity(request.getStockQuantity());

        return toResponse(productRepository.save(product));
    }

    @Transactional
    public void deleteProduct(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Product", "id", id));
        product.setActive(false);          // soft delete
        productRepository.save(product);
    }

    public Page<ProductDtos.ProductResponse> searchProducts(String keyword, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return productRepository.searchByName(keyword, pageable).map(this::toResponse);
    }
}
