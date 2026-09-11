package com.example.grocyassistant.assistant

import android.content.Context
import com.example.grocyassistant.data.grocy.GrocyProductGroup
import com.example.grocyassistant.data.grocy.GrocyProductGroups

class ProductGroupResolver(
    context: Context
) {
    private val groupsApi =
        GrocyProductGroups(context)

    suspend fun resolve(
        search: String
    ): GrocyProductGroup? {

        val query =
            search.trim().lowercase()

        if (query.isEmpty()) {
            return null
        }

        val groups =
            groupsApi.getProductGroups()

        return groups.firstOrNull {
            it.name.trim().lowercase() == query
        } ?: groups.firstOrNull {
            it.name.trim().lowercase().startsWith(query)
        } ?: groups.firstOrNull {
            it.name.trim().lowercase().contains(query)
        }
    }
}