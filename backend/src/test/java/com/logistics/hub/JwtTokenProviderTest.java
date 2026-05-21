package com.logistics.hub;

import com.logistics.hub.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Collections;

import static org.assertj.core.api.Assertions.assertThat;

class JwtTokenProviderTest {

    private JwtTokenProvider jwtTokenProvider;
    private UserDetails userDetails;

    // A valid Base64-encoded HMAC-SHA256 key (at least 256 bits)
    // "3cfa76ef14937c1c0ea519f8fc057a80fcd04a7420f8e8bcd0a7567c272e007b" is hex.
    // Let's use a standard base64 key or decode hex. Wait, in JwtTokenProvider:
    // Decoders.BASE64.decode(jwtSecret);
    // So the secret in app.jwt.secret MUST be Base64 encoded.
    // Let's generate/use a valid base64 key of 256 bits or more:
    // e.g., "dGhpcy1pcy1hLXNlY3JldC1rZXktZm9yLWp3dC10b2tlbi1nZW5lcmF0aW9uLWluLW91ci1hcHA="
    private final String base64Secret = "dGhpcy1pcy1hLXNlY3JldC1rZXktZm9yLWp3dC10b2tlbi1nZW5lcmF0aW9uLWluLW91ci1hcHA=";

    @BeforeEach
    void setUp() {
        jwtTokenProvider = new JwtTokenProvider();
        ReflectionTestUtils.setField(jwtTokenProvider, "jwtSecret", base64Secret);
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
        ReflectionTestUtils.setField(expiredProvider, "jwtSecret", base64Secret);
        ReflectionTestUtils.setField(expiredProvider, "jwtExpirationMs", -1000L); // expired 1s ago

        String token = expiredProvider.generateToken(userDetails);
        boolean isValid = expiredProvider.validateToken(token);
        assertThat(isValid).isFalse();
    }
}
