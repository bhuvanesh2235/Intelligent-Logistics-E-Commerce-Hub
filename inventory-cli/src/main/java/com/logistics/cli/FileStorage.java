package com.logistics.cli;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * FileStorage — handles JSON read/write operations for inventory persistence.
 */
public class FileStorage {

    private final ObjectMapper mapper;
    private final File dataFile;

    public FileStorage(String filePath) {
        this.mapper = new ObjectMapper()
                .enable(SerializationFeature.INDENT_OUTPUT);
        this.dataFile = new File(filePath);
        ensureDirectoryExists();
    }

    private void ensureDirectoryExists() {
        File parent = dataFile.getParentFile();
        if (parent != null && !parent.exists()) {
            parent.mkdirs();
        }
        if (!dataFile.exists()) {
            try {
                mapper.writeValue(dataFile, new ArrayList<>());
            } catch (IOException e) {
                throw new RuntimeException("Failed to create inventory file: " + e.getMessage());
            }
        }
    }

    public List<Product> loadAll() {
        try {
            return mapper.readValue(dataFile, new TypeReference<List<Product>>() {});
        } catch (IOException e) {
            System.err.println("⚠ Warning: Could not read inventory file. Starting fresh.");
            return new ArrayList<>();
        }
    }

    public void saveAll(List<Product> products) {
        try {
            mapper.writeValue(dataFile, products);
        } catch (IOException e) {
            throw new RuntimeException("Failed to save inventory: " + e.getMessage());
        }
    }
}
