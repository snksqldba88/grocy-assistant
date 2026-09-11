package com.example.grocyassistant.assistant

import android.content.Context
import com.example.grocyassistant.data.grocy.GrocyProduct
import com.example.grocyassistant.data.grocy.GrocyProductRepository

class ProductResolver(
    context: Context
) {

    private val repository =
        GrocyProductRepository(context)

    private val matcher =
        ProductMatcher()

    suspend fun resolve(
        search: String
    ): GrocyProduct? {

        val products =
            repository.findProducts(search)

        return matcher.findMatch(
            products = products,
            search = search
        )
    }
}