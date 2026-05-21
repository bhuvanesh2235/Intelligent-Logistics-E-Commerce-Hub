package com.logistics.hub;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.logistics.hub.controller.ProductController;
import com.logistics.hub.dto.ProductDtos;
import com.logistics.hub.exception.GlobalExceptionHandler;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.service.ProductService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.math.BigDecimal;
import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class ProductControllerTest {

    private MockMvc mockMvc;

    @Mock
    private ProductService productService;

    @InjectMocks
    private ProductController productController;

    private ObjectMapper objectMapper = new ObjectMapper();
    private ProductDtos.ProductResponse productResponse;
    private ProductDtos.ProductRequest productRequest;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(productController)
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();

        productResponse = new ProductDtos.ProductResponse();
        productResponse.setId(1L);
        productResponse.setSku("ELEC-123");
        productResponse.setName("Smartphone");
        productResponse.setPrice(BigDecimal.valueOf(500.00));
        productResponse.setStockQuantity(50);
        productResponse.setActive(true);

        productRequest = new ProductDtos.ProductRequest();
        productRequest.setSku("ELEC-123");
        productRequest.setName("Smartphone");
        productRequest.setCategoryId(1L);
        productRequest.setCost(BigDecimal.valueOf(400.00));
        productRequest.setPrice(BigDecimal.valueOf(500.00));
        productRequest.setWeightGrams(200);
        productRequest.setStockQuantity(50);
    }

    @Test
    void getAll_withoutSearch_success() throws Exception {
        Page<ProductDtos.ProductResponse> page = new PageImpl<>(Collections.singletonList(productResponse), PageRequest.of(0, 12), 1);
        when(productService.getAllProducts(anyInt(), anyInt())).thenReturn(page);

        mockMvc.perform(get("/api/products")
                        .param("page", "0")
                        .param("size", "12"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].id").value(1L))
                .andExpect(jsonPath("$.content[0].name").value("Smartphone"));
    }

    @Test
    void getAll_withSearch_success() throws Exception {
        Page<ProductDtos.ProductResponse> page = new PageImpl<>(Collections.singletonList(productResponse), PageRequest.of(0, 12), 1);
        when(productService.searchProducts(eq("Smart"), anyInt(), anyInt())).thenReturn(page);

        mockMvc.perform(get("/api/products")
                        .param("search", "Smart")
                        .param("page", "0")
                        .param("size", "12"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].name").value("Smartphone"));
    }

    @Test
    void getById_success() throws Exception {
        when(productService.getProductById(1L)).thenReturn(productResponse);

        mockMvc.perform(get("/api/products/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.name").value("Smartphone"));
    }

    @Test
    void getById_notFound_returnsNotFound() throws Exception {
        when(productService.getProductById(99L)).thenThrow(new ResourceNotFoundException("Product", "id", 99L));

        mockMvc.perform(get("/api/products/99"))
                .andExpect(status().isNotFound());
    }

    @Test
    void create_success() throws Exception {
        when(productService.createProduct(any(ProductDtos.ProductRequest.class))).thenReturn(productResponse);

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(productRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.sku").value("ELEC-123"));
    }

    @Test
    void create_invalidInputs_returnsBadRequest() throws Exception {
        ProductDtos.ProductRequest invalidRequest = new ProductDtos.ProductRequest();
        invalidRequest.setSku(""); // Invalid SKU
        invalidRequest.setName(""); // Invalid Name

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void update_success() throws Exception {
        when(productService.updateProduct(eq(1L), any(ProductDtos.ProductRequest.class))).thenReturn(productResponse);

        mockMvc.perform(put("/api/products/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(productRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L));
    }

    @Test
    void delete_success() throws Exception {
        doNothing().when(productService).deleteProduct(1L);

        mockMvc.perform(delete("/api/products/1"))
                .andExpect(status().isNoContent());

        verify(productService).deleteProduct(1L);
    }
}
