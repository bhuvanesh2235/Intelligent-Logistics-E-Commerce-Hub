package com.logistics.hub.service;

import com.logistics.hub.dto.AuthDtos;
import com.logistics.hub.entity.User;
import com.logistics.hub.exception.ResourceNotFoundException;
import com.logistics.hub.repository.UserRepository;
import com.logistics.hub.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManager authenticationManager;
    private final CustomUserDetailsService userDetailsService;

    @Transactional
    public AuthDtos.AuthResponse register(AuthDtos.RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername()))
            throw new IllegalArgumentException("Username already taken: " + request.getUsername());
        if (userRepository.existsByEmail(request.getEmail()))
            throw new IllegalArgumentException("Email already registered: " + request.getEmail());

        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .role(User.Role.CUSTOMER)
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .isActive(true)
                .build();

        user = userRepository.save(user);
        UserDetails userDetails = userDetailsService.loadUserByUsername(user.getUsername());
        String token = jwtTokenProvider.generateToken(userDetails);
        return new AuthDtos.AuthResponse(token, user.getUsername(), user.getEmail(),
                user.getRole().name(), user.getId());
    }

    public AuthDtos.AuthResponse login(AuthDtos.LoginRequest request) {
        Authentication auth = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword()));

        UserDetails userDetails = (UserDetails) auth.getPrincipal();
        String token = jwtTokenProvider.generateToken(userDetails);
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new ResourceNotFoundException("User", "username", request.getUsername()));

        return new AuthDtos.AuthResponse(token, user.getUsername(), user.getEmail(),
                user.getRole().name(), user.getId());
    }
}
