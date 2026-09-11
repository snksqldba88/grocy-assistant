package com.example.grocyassistant.data.grocy

data class GrocyProduct(
    val id: Int,
    val name: String,
    val description: String?,
    val groupId: Int?,
    val locationId: Int?,
    val quIdPurchase: Int?,
    val quIdStock: Int?
)