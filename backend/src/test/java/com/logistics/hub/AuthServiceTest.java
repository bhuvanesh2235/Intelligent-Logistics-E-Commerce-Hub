package com.logistics.hub;

import com.logistics.hub.entity.User;
import com.logistics.hub.repository.UserRepository;
import com.logistics.hub.security.JwtTokenProvider;
import com.logistics.hub.service.AuthService;
import com.logistics.hub.service.CustomUserDetailsService;
import com.logistics.hub.dto.AuthDtos;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock private UserRepository userRepository;
    @Mock private JwtTokenProvider jwtTokenProvider;
    @Mock private AuthenticationManager authenticationManager;
    @Mock private CustomUserDetailsService userDetailsService;

    @Spy private PasswordEncoder passwordEncoder = new BCryptPasswordEncoder(4);

    @InjectMocks private AuthService authService;

    private AuthDtos.RegisterRequest registerRequest;

    @BeforeEach
    void setUp() {
        registerRequest = new AuthDtos.RegisterRequest();
        registerRequest.setUsername("testuser");
        registerRequest.setEmail("test@example.com");
        registerRequest.setPassword("Password@123");
        registerRequest.setFullName("Test User");
    }

    @Test
    void register_success() {
        when(userRepository.existsByUsername("testuser")).thenReturn(false);
        when(userRepository.existsByEmail("test@example.com")).thenReturn(false);

        User savedUser = User.builder()
                .id(1L).username("testuser").email("test@example.com")
                .role(User.Role.CUSTOMER).fullName("Test User")
                .passwordHash("hashed").isActive(true).build();
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        UserDetails ud = new org.springframework.security.core.userdetails.User(
                "testuser", "hashed", List.of());
        when(userDetailsService.loadUserByUsername("testuser")).thenReturn(ud);
        when(jwtTokenProvider.generateToken(ud)).thenReturn("mock-token");

        AuthDtos.AuthResponse response = authService.register(registerRequest);

        assertThat(response.getToken()).isEqualTo("mock-token");
        assertThat(response.getUsername()).isEqualTo("testuser");
        assertThat(response.getRole()).isEqualTo("CUSTOMER");
        verify(userRepository).save(any(User.class));
    }

    @Test
    void register_duplicateUsername_throws() {
        when(userRepository.existsByUsername("testuser")).thenReturn(true);
        assertThatThrownBy(() -> authService.register(registerRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Username already taken");
    }

    @Test
    void login_success() {
        AuthDtos.LoginRequest loginRequest = new AuthDtos.LoginRequest();
        loginRequest.setUsername("testuser");
        loginRequest.setPassword("Password@123");

        UserDetails ud = new org.springframework.security.core.userdetails.User(
                "testuser", "hashed", List.of());
        Authentication auth = mock(Authentication.class);
        when(auth.getPrincipal()).thenReturn(ud);
        when(authenticationManager.authenticate(any())).thenReturn(auth);
        when(jwtTokenProvider.generateToken(ud)).thenReturn("login-token");

        User user = User.builder().id(1L).username("testuser").email("test@example.com")
                .role(User.Role.CUSTOMER).build();
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(user));

        AuthDtos.AuthResponse response = authService.login(loginRequest);

        assertThat(response.getToken()).isEqualTo("login-token");
        assertThat(response.getUsername()).isEqualTo("testuser");
    }
}
