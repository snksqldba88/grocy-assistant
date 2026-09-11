package com.example.grocyassistant.assistant

import android.content.Context
import com.example.grocyassistant.data.grocy.GrocyStock

class StockGroupQuery(
    context: Context
) {
    private val stockApi =
        com.example.grocyassistant.data.grocy.GrocyStockApi(context)

    private val groupResolver =
        ProductGroupResolver(context)

    suspend fun findStockByGroup(
        search: String
    ): List<GrocyStock> {

        val group =
            groupResolver.resolve(search)
                ?: return emptyList()

        val stock =
            stockApi.getStock()

        return stock.filter {
            it.productGroupId == group.id
        }
    }
}