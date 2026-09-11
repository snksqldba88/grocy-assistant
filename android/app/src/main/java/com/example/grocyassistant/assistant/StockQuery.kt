package com.example.grocyassistant.assistant

import android.content.Context
import com.example.grocyassistant.data.grocy.GrocyStock
import com.example.grocyassistant.data.grocy.GrocyStockApi

class StockQuery(
    context: Context
) {

    private val stockApi =
        GrocyStockApi(context)

    private val productResolver =
        ProductResolver(context)

    suspend fun findStock(
        search: String
    ): GrocyStock? {

        val product =
            productResolver.resolve(search)
                ?: return null

        val stock =
            stockApi.getStock()

        return stock.firstOrNull {
            it.productId == product.id
        }
    }
}