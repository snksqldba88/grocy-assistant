package com.example.grocyassistant.assistant

import com.example.grocyassistant.data.grocy.GrocyProduct

class ProductMatcher {

    fun findMatch(
        products: List<GrocyProduct>,
        search: String
    ): GrocyProduct? {

        val query =
            search.trim().lowercase()

        if (query.isEmpty()) {
            return null
        }

        // Exact match first
        products.firstOrNull {
            it.name.trim().lowercase() == query
        }?.let {
            return it
        }

        // Then prefix match
        products.firstOrNull {
            it.name.trim().lowercase()
                .startsWith(query)
        }?.let {
            return it
        }

        // Finally, contains match
        products.firstOrNull {
            it.name.trim().lowercase()
                .contains(query)
        }?.let {
            return it
        }

        return null
    }
}