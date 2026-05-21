package com.logistics.hub;

import com.logistics.hub.dto.ProductDtos;
import com.logistics.hub.entity.Category;
import com.logistics.hub.entity.Product;
import com.logistics.hub.entity.Warehouse;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.ProductRepository;
import com.logistics.hub.service.ProductService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.*;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    private Product product;
    private ProductDtos.ProductRequest productRequest;

    @BeforeEach
    void setUp() {
        Category category = new Category();
        category.setId(1L);
        category.setName("Electronics");

        Warehouse warehouse = new Warehouse();
        warehouse.setId(1L);
        warehouse.setName("Alpha Warehouse");

        product = Product.builder()
                .id(1L)
                .sku("SKU-123")
                .name("Test Product")
                .description("Test Description")
                .category(category)
                .cost(BigDecimal.valueOf(10.00))
                .price(BigDecimal.valueOf(15.00))
                .weightGrams(500)
                .importance(Product.Importance.MEDIUM)
                .stockQuantity(100)
                .warehouse(warehouse)
                .isActive(true)
                .build();

        productRequest = new ProductDtos.ProductRequest();
        productRequest.setSku("SKU-123");
        productRequest.setName("Test Product");
        productRequest.setDescription("Test Description");
        productRequest.setCategoryId(1L);
        productRequest.setCost(BigDecimal.valueOf(10.00));
        productRequest.setPrice(BigDecimal.valueOf(15.00));
        productRequest.setWeightGrams(500);
        productRequest.setImportance(Product.Importance.MEDIUM);
        productRequest.setStockQuantity(100);
        productRequest.setWarehouseId(1L);
    }

    @Test
    void getAllProducts_success() {
        Pageable pageable = PageRequest.of(0, 12, Sort.by("createdAt").descending());
        Page<Product> page = new PageImpl<>(Collections.singletonList(product), pageable, 1);
        when(productRepository.findByIsActiveTrue(pageable)).thenReturn(page);

        Page<ProductDtos.ProductResponse> result = productService.getAllProducts(0, 12);

        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).getSku()).isEqualTo("SKU-123");
        verify(productRepository).findByIsActiveTrue(pageable);
    }

    @Test
    void getProductById_success() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        ProductDtos.ProductResponse response = productService.getProductById(1L);

        assertThat(response).isNotNull();
        assertThat(response.getId()).isEqualTo(1L);
        assertThat(response.getName()).isEqualTo("Test Product");
    }

    @Test
    void getProductById_notFound_throwsException() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.getProductById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Product not found with id: '99'");
    }

    @Test
    void createProduct_success() {
        when(productRepository.existsBySku("SKU-123")).thenReturn(false);
        when(productRepository.save(any(Product.class))).thenReturn(product);

        ProductDtos.ProductResponse response = productService.createProduct(productRequest);

        assertThat(response).isNotNull();
        assertThat(response.getSku()).isEqualTo("SKU-123");
        verify(productRepository).save(any(Product.class));
    }

    @Test
    void createProduct_duplicateSku_throwsException() {
        when(productRepository.existsBySku("SKU-123")).thenReturn(true);

        assertThatThrownBy(() -> productService.createProduct(productRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("SKU already exists");
        verify(productRepository, never()).save(any(Product.class));
    }

    @Test
    void updateProduct_success() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(productRepository.save(any(Product.class))).thenReturn(product);

        ProductDtos.ProductResponse response = productService.updateProduct(1L, productRequest);

        assertThat(response).isNotNull();
        assertThat(response.getId()).isEqualTo(1L);
        verify(productRepository).save(product);
    }

    @Test
    void updateProduct_notFound_throwsException() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.updateProduct(99L, productRequest))
                .isInstanceOf(ResourceNotFoundException.class);
        verify(productRepository, never()).save(any(Product.class));
    }

    @Test
    void deleteProduct_success() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(productRepository.save(any(Product.class))).thenReturn(product);

        productService.deleteProduct(1L);

        assertThat(product.isActive()).isFalse();
        verify(productRepository).save(product);
    }

    @Test
    void deleteProduct_notFound_throwsException() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.deleteProduct(99L))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    void searchProducts_success() {
        Pageable pageable = PageRequest.of(0, 10);
        Page<Product> page = new PageImpl<>(Collections.singletonList(product), pageable, 1);
        when(productRepository.searchByName("test", pageable)).thenReturn(page);

        Page<ProductDtos.ProductResponse> result = productService.searchProducts("test", 0, 10);

        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        verify(productRepository).searchByName("test", pageable);
    }
}
