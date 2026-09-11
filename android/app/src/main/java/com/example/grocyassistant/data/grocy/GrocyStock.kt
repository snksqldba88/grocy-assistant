package com.example.grocyassistant.data.grocy

import android.content.Context
import org.json.JSONArray

data class GrocyStock(
    val productId: Int,
    val productName: String,
    val amount: Double,
    val unitId: Int?,
    val locationId: Int?,
    val productGroupId: Int?
)

class GrocyStockApi(
    context: Context
) {

    private val api =
        GrocyApi(context)

    suspend fun getStock(): List<GrocyStock> {

        val json =
            api.getArray(
                "/api/stock"
            )

        return json.toStockList()
    }

    private fun JSONArray.toStockList():
            List<GrocyStock> {

        val stock =
            mutableListOf<GrocyStock>()

        for (index in 0 until length()) {

            val item =
                getJSONObject(index)

            val product =
                item.optJSONObject("product")

            if (product == null) {
                continue
            }

            stock.add(
                GrocyStock(
                    productId =
                        item.optString("product_id")
                            .toIntOrNull()
                            ?: product.optString("id")
                                .toIntOrNull()
                            ?: 0,

                    productName =
                        product.optString("name"),

                    amount =
                        item.optString("amount")
                            .toDoubleOrNull()
                            ?: 0.0,

                    unitId =
                        product.optString("qu_id_stock")
                            .toIntOrNull(),

                    locationId =
                        product.optString("location_id")
                            .toIntOrNull(),

                    productGroupId =
                        product.optString("product_group_id")
                            .toIntOrNull()
                )
            )
        }

        return stock
    }
}