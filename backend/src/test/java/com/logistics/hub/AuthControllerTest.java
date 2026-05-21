package com.logistics.hub;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.logistics.hub.controller.AuthController;
import com.logistics.hub.dto.AuthDtos;
import com.logistics.hub.exception.GlobalExceptionHandler;
import com.logistics.hub.service.AuthService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class AuthControllerTest {

    private MockMvc mockMvc;

    @Mock
    private AuthService authService;

    @InjectMocks
    private AuthController authController;

    private ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(authController)
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
    }

    @Test
    void register_success() throws Exception {
        AuthDtos.RegisterRequest request = new AuthDtos.RegisterRequest();
        request.setUsername("testadmin");
        request.setEmail("admin@test.com");
        request.setPassword("Password@123");
        request.setFullName("Test Admin");

        AuthDtos.AuthResponse response = new AuthDtos.AuthResponse(
                "mock-token", "testadmin", "admin@test.com", "ADMIN", 1L
        );

        when(authService.register(any(AuthDtos.RegisterRequest.class))).thenReturn(response);

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.token").value("mock-token"))
                .andExpect(jsonPath("$.username").value("testadmin"))
                .andExpect(jsonPath("$.role").value("ADMIN"));
    }

    @Test
    void register_validationFailure_returnsBadRequest() throws Exception {
        AuthDtos.RegisterRequest request = new AuthDtos.RegisterRequest();
        // invalid field inputs (blank username, invalid email, short password)
        request.setUsername("");
        request.setEmail("invalid-email");
        request.setPassword("short");
        request.setFullName("");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void login_success() throws Exception {
        AuthDtos.LoginRequest request = new AuthDtos.LoginRequest();
        request.setUsername("testadmin");
        request.setPassword("Password@123");

        AuthDtos.AuthResponse response = new AuthDtos.AuthResponse(
                "mock-token", "testadmin", "admin@test.com", "ADMIN", 1L
        );

        when(authService.login(any(AuthDtos.LoginRequest.class))).thenReturn(response);

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").value("mock-token"))
                .andExpect(jsonPath("$.username").value("testadmin"));
    }

    @Test
    void login_blankCredentials_returnsBadRequest() throws Exception {
        AuthDtos.LoginRequest request = new AuthDtos.LoginRequest();
        request.setUsername("");
        request.setPassword("");

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }
}
