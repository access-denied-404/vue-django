<template>
  <div class="panel panel-info">
    <div class="panel-heading">Информация о факторинговом продукте</div>
    <div class="panel-body">

      <div class="row">
        <div class="col-md-6">
          <label>Требуемый факторинговый продукт</label>
          <checkbox :name="'factoring_product_is_regressive'" v-model="factoring_product_is_regressive" type="primary">Регрессивный факторинг</checkbox>
          <checkbox :name="'factoring_product_is_not_regressive'" v-model="factoring_product_is_not_regressive" type="primary">Факторинг без регресса</checkbox>
          <checkbox :name="'factoring_product_is_cred_risks_cover'" v-model="factoring_product_is_cred_risks_cover" type="primary">Покрытие кредитных рисков</checkbox>
          <checkbox :name="'factoring_product_is_suppliers_financing'" v-model="factoring_product_is_suppliers_financing" type="primary">Финансирование поставщиков</checkbox>
          <checkbox :name="'factoring_product_is_orders_financing'" v-model="factoring_product_is_orders_financing" type="primary">Финансирование заказов</checkbox>
          <checkbox :name="'factoring_product_is_closed'" v-model="factoring_product_is_closed" type="primary">Закрытый факторинг</checkbox>
          <checkbox :name="'factoring_product_is_export'" v-model="factoring_product_is_export" type="primary">Экспортный факторинг</checkbox>
          <checkbox :name="'factoring_product_is_import'" v-model="factoring_product_is_import" type="primary">Импортный факторинг</checkbox>
        </div>

        <div class="col-md-6">
          <bs-input :name="'factoring_avg_actual_buyers_payment_term'" v-model="factoring_avg_actual_buyers_payment_term" :type="'number'" :label="'Средний фактический срок оплаты покупателями (дней)'"></bs-input>
          <bs-input :name="'factoring_max_contract_deferred_payment_term'" v-model="factoring_max_contract_deferred_payment_term" :type="'number'" :label="'Максимальный период отсрочки платежа по контрактам (дней)'"></bs-input>
        </div>
      </div>

      <div class="row">
        <div class="col-md-12"><bs-input :name="'factoring_sale_goods_or_services'" v-model="factoring_sale_goods_or_services" :label="'Виды реализуемых товаров/услуг'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-12"><bs-input :name="'factoring_manufactured_goods'" v-model="factoring_manufactured_goods" :label="'Виды производимых товаров'"></bs-input></div>
      </div>

    </div>
  </div>
</template>

<script>
  import {input, checkbox} from 'vue-strap'

  export default {
    name: 'form-factoring',
    components: {
      'bs-input': input,
      'checkbox': checkbox
    },
    data () {
      var regData = JSON.parse(window.regdata)

      if (regData !== null && regData.formdata !== null) {
        return {
          factoring_product_is_regressive: regData.formdata.factoring_product_is_regressive,
          factoring_product_is_not_regressive: regData.formdata.factoring_product_is_not_regressive,
          factoring_product_is_cred_risks_cover: regData.formdata.factoring_product_is_cred_risks_cover,
          factoring_product_is_suppliers_financing: regData.formdata.factoring_product_is_suppliers_financing,
          factoring_product_is_orders_financing: regData.formdata.factoring_product_is_orders_financing,
          factoring_product_is_closed: regData.formdata.factoring_product_is_closed,
          factoring_product_is_export: regData.formdata.factoring_product_is_export,
          factoring_product_is_import: regData.formdata.factoring_product_is_import,
          factoring_avg_actual_buyers_payment_term: regData.formdata.factoring_avg_actual_buyers_payment_term,
          factoring_max_contract_deferred_payment_term: regData.formdata.factoring_max_contract_deferred_payment_term,
          factoring_sale_goods_or_services: regData.formdata.factoring_sale_goods_or_services,
          factoring_manufactured_goods: regData.formdata.factoring_manufactured_goods
        }
      } else {
        return {
          factoring_product_is_regressive: '',
          factoring_product_is_not_regressive: '',
          factoring_product_is_cred_risks_cover: '',
          factoring_product_is_suppliers_financing: '',
          factoring_product_is_orders_financing: '',
          factoring_product_is_closed: '',
          factoring_product_is_export: '',
          factoring_product_is_import: '',
          factoring_avg_actual_buyers_payment_term: '',
          factoring_max_contract_deferred_payment_term: '',
          factoring_sale_goods_or_services: '',
          factoring_manufactured_goods: ''
        }
      }
    }
  }
</script>
