package com.logistics.hub.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

public class AuthDtos {

    @Data
    public static class RegisterRequest {
        @NotBlank @Size(min = 3, max = 50)
        private String username;

        @NotBlank @Email
        private String email;

        @NotBlank @Size(min = 8, max = 100)
        private String password;

        @NotBlank
        private String fullName;

        private String phone;
    }

    @Data
    public static class LoginRequest {
        @NotBlank private String username;
        @NotBlank private String password;
    }

    @Data
    public static class AuthResponse {
        private String token;
        private String tokenType = "Bearer";
        private String username;
        private String email;
        private String role;
        private Long userId;

        public AuthResponse(String token, String username, String email,
                            String role, Long userId) {
            this.token = token;
            this.username = username;
            this.email = email;
            this.role = role;
            this.userId = userId;
        }
    }
}
