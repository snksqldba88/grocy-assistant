package com.example.grocyassistant.data.grocy

import android.content.Context

class GrocyProductRepository(
    context: Context
) {

    private val products =
        GrocyProducts(context)

    suspend fun findProducts(
        search: String
    ): List<GrocyProduct> {
        return products.findProducts(search)
    }
}