package com.example.grocyassistant.data.grocy

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

class GrocyProducts(
    context: Context
) {

    private val api =
        GrocyApi(context)

    suspend fun findProducts(
        search: String
    ): List<GrocyProduct> {

        val encodedSearch =
            java.net.URLEncoder.encode(
                "name~${search.trim()}",
                "UTF-8"
            )

        val json =
            api.getArray(
                "/api/objects/products?query[]=$encodedSearch"
            )

        return json.toProductList()
    }

    private fun JSONArray.toProductList():
            List<GrocyProduct> {

        val products =
            mutableListOf<GrocyProduct>()

        for (index in 0 until length()) {

            val item =
                getJSONObject(index)

            products.add(
                GrocyProduct(
                    id = item.optString("id")
                        .toIntOrNull() ?: 0,

                    name = item.optString("name"),

                    description =
                        item.optString("description")
                            .takeIf { it.isNotEmpty() },

                    groupId =
                        item.optString("product_group_id")
                            .toIntOrNull(),

                    locationId =
                        item.optString("location_id")
                            .toIntOrNull(),

                    quIdPurchase =
                        item.optString("qu_id_purchase")
                            .toIntOrNull(),

                    quIdStock =
                        item.optString("qu_id_stock")
                            .toIntOrNull()
                )
            )
        }

        return products
    }
}