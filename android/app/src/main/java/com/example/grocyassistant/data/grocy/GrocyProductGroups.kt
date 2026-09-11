package com.example.grocyassistant.data.grocy

import android.content.Context
import org.json.JSONArray

data class GrocyProductGroup(
    val id: Int,
    val name: String
)

class GrocyProductGroups(
    context: Context
) {
    private val api = GrocyApi(context)

    suspend fun getProductGroups(): List<GrocyProductGroup> {
        val json =
            api.getArray("/api/objects/product_groups")

        return json.toProductGroupList()
    }

    private fun JSONArray.toProductGroupList():
            List<GrocyProductGroup> {

        val groups = mutableListOf<GrocyProductGroup>()

        for (index in 0 until length()) {
            val item = getJSONObject(index)

            groups.add(
                GrocyProductGroup(
                    id =
                        item.optString("id")
                            .toIntOrNull()
                            ?: 0,

                    name =
                        item.optString("name")
                )
            )
        }

        return groups
    }
}