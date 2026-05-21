package com.logistics.hub.controller;

import com.logistics.hub.repository.OrderRepository;
import com.logistics.hub.repository.ProductRepository;
import com.logistics.hub.repository.ShipmentRepository;
import com.logistics.hub.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final UserRepository userRepository;
    private final ShipmentRepository shipmentRepository;

    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, Object>> getDashboard() {
        Map<String, Object> dashboard = new HashMap<>();

        // KPIs
        dashboard.put("totalOrders", orderRepository.count());
        dashboard.put("totalProducts", productRepository.count());
        dashboard.put("totalUsers", userRepository.count());
        dashboard.put("totalShipments", shipmentRepository.count());

        // Orders by status
        List<Object[]> ordersByStatus = orderRepository.countGroupByStatus();
        Map<String, Long> statusMap = new HashMap<>();
        ordersByStatus.forEach(row -> statusMap.put(row[0].toString(), (Long) row[1]));
        dashboard.put("ordersByStatus", statusMap);

        // Shipments by mode
        List<Object[]> shipmentsByMode = shipmentRepository.countByMode();
        Map<String, Long> modeMap = new HashMap<>();
        shipmentsByMode.forEach(row -> modeMap.put(row[0].toString(), (Long) row[1]));
        dashboard.put("shipmentsByMode", modeMap);

        // On-time delivery rate
        Double onTimeRate = shipmentRepository.getOnTimeDeliveryRate();
        dashboard.put("onTimeDeliveryRate", onTimeRate != null
                ? Math.round(onTimeRate * 10000.0) / 100.0 : 0.0);

        return ResponseEntity.ok(dashboard);
    }
}
