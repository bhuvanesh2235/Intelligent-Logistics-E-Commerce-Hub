package com.logistics.hub;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class LogisticsHubApplication {
    public static void main(String[] args) {
        SpringApplication.run(LogisticsHubApplication.class, args);
    }
}
