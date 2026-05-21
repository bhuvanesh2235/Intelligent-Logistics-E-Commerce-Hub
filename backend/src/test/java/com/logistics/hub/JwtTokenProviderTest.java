package com.logistics.hub;

import com.logistics.hub.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.test.util.ReflectionTestUtils;

import java.security.SecureRandom;
import java.util.Base64;
import java.util.Collections;

import static org.assertj.core.api.Assertions.assertThat;

class JwtTokenProviderTest {

    private JwtTokenProvider jwtTokenProvider;
    private UserDetails userDetails;

    /** Randomly generated per test run — never stored in source control. */
    private String testBase64Secret;

    @BeforeEach
    void setUp() {
        // Generate a fresh 256-bit (32-byte) random secret for every test run
        byte[] keyBytes = new byte[32];
        new SecureRandom().nextBytes(keyBytes);
        testBase64Secret = Base64.getEncoder().encodeToString(keyBytes);

        jwtTokenProvider = new JwtTokenProvider();
        ReflectionTestUtils.setField(jwtTokenProvider, "jwtSecret", testBase64Secret);
        ReflectionTestUtils.setField(jwtTokenProvider, "jwtExpirationMs", 3600000L); // 1 hour

        userDetails = new User("testadmin", "password", Collections.emptyList());
    }

    @Test
    void generateToken_success() {
        String token = jwtTokenProvider.generateToken(userDetails);
        assertThat(token).isNotBlank();
    }

    @Test
    void getUsernameFromToken_success() {
        String token = jwtTokenProvider.generateToken(userDetails);
        String username = jwtTokenProvider.getUsernameFromToken(token);
        assertThat(username).isEqualTo("testadmin");
    }

    @Test
    void validateToken_success() {
        String token = jwtTokenProvider.generateToken(userDetails);
        boolean isValid = jwtTokenProvider.validateToken(token);
        assertThat(isValid).isTrue();
    }

    @Test
    void validateToken_invalidToken_returnsFalse() {
        boolean isValid = jwtTokenProvider.validateToken("invalid.jwt.token");
        assertThat(isValid).isFalse();
    }

    @Test
    void validateToken_expiredToken_returnsFalse() {
        // Create token provider with 0ms expiration
        JwtTokenProvider expiredProvider = new JwtTokenProvider();
        ReflectionTestUtils.setField(expiredProvider, "jwtSecret", testBase64Secret);
        ReflectionTestUtils.setField(expiredProvider, "jwtExpirationMs", -1000L); // expired 1s ago

        String token = expiredProvider.generateToken(userDetails);
        boolean isValid = expiredProvider.validateToken(token);
        assertThat(isValid).isFalse();
    }
}
