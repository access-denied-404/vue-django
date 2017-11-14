<template>
  <div class="panel panel-info">
    <div class="panel-heading">Информация о лизинговом продукте</div>
    <div class="panel-body">

      <div class="row">
        <div class="col-md-3"><bs-input :name="'leasing_term'" v-model="leasing_term" :type="'number'" :label="'Срок лизинга (мес.)'"></bs-input></div>
        <div class="col-md-4"><bs-input :name="'leasing_advance_payment_rate'" v-model="leasing_advance_payment_rate" :label="'Авансовый платеж (%)'"></bs-input></div>
        <div class="col-md-5"><bs-input :name="'leasing_payment_schedule'" v-model="leasing_payment_schedule" :label="'График платежей'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-12"><bs-input :name="'leasing_asset_operation_territory'" v-model="leasing_asset_operation_territory" :label="'Территория эксплуатации предмета лизинга'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-6"><bs-input :name="'leasing_bank_account_number'" v-model="leasing_bank_account_number" :label="'Рассчетный счет заявителя'"></bs-input></div>
        <div class="col-md-6"><bs-input :name="'leasing_corr_account_number'" v-model="leasing_corr_account_number" :label="'Корреспондентский счет'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-9"><bs-input :name="'leasing_bank_name'" v-model="leasing_bank_name" :label="'Банк'"></bs-input></div>
        <div class="col-md-3"><bs-input :name="'leasing_bank_identification_code'" v-model="leasing_bank_identification_code" :label="'БИК'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-12"><bs-input :name="'leasing_holder_on_balance_name'" v-model="leasing_holder_on_balance_name" :label="'Балансодержатель'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-4"><bs-input :name="'leasing_holder_on_balance_ogrn'" v-model="leasing_holder_on_balance_ogrn" :label="'ОГРН балансодержателя'"></bs-input></div>
        <div class="col-md-4"><bs-input :name="'leasing_holder_on_balance_inn'" v-model="leasing_holder_on_balance_inn" :label="'ИНН балансодержателя'"></bs-input></div>
        <div class="col-md-4"><bs-input :name="'leasing_holder_on_balance_kpp'" v-model="leasing_holder_on_balance_kpp" :label="'КПП балансодержателя'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-12"><bs-input :name="'leasing_insurer_name'" v-model="leasing_insurer_name" :label="'Страхователь'"></bs-input></div>
      </div>

      <div class="row">
        <div class="col-md-4"><bs-input :name="'leasing_insurer_ogrn'" v-model="leasing_insurer_ogrn" :label="'ОГРН страхователя'"></bs-input></div>
        <div class="col-md-4"><bs-input :name="'leasing_insurer_inn'" v-model="leasing_insurer_inn" :label="'ИНН страхователя'"></bs-input></div>
        <div class="col-md-4"><bs-input :name="'leasing_insurer_kpp'" v-model="leasing_insurer_kpp" :label="'КПП страхователя'"></bs-input></div>
      </div>

    </div>
  </div>
</template>

<script>
  import {input} from 'vue-strap'

  export default {
    name: 'form-leasing',
    components: {
      'bs-input': input
    },
    data () {
      var regData = JSON.parse(window.regdata)

      if (regData !== null && regData.formdata !== null) {
        return {
          leasing_term: regData.formdata.leasing_term,
          leasing_advance_payment_rate: regData.formdata.leasing_advance_payment_rate,
          leasing_payment_schedule: regData.formdata.leasing_payment_schedule,
          leasing_asset_operation_territory: regData.formdata.leasing_asset_operation_territory,
          leasing_bank_account_number: regData.formdata.leasing_bank_account_number,
          leasing_corr_account_number: regData.formdata.leasing_corr_account_number,
          leasing_bank_name: regData.formdata.leasing_bank_name,
          leasing_bank_identification_code: regData.formdata.leasing_bank_identification_code,
          leasing_holder_on_balance_name: regData.formdata.leasing_holder_on_balance_name,
          leasing_holder_on_balance_ogrn: regData.formdata.leasing_holder_on_balance_ogrn,
          leasing_holder_on_balance_inn: regData.formdata.leasing_holder_on_balance_inn,
          leasing_holder_on_balance_kpp: regData.formdata.leasing_holder_on_balance_kpp,
          leasing_insurer_name: regData.formdata.leasing_insurer_name,
          leasing_insurer_ogrn: regData.formdata.leasing_insurer_ogrn,
          leasing_insurer_inn: regData.formdata.leasing_insurer_inn,
          leasing_insurer_kpp: regData.formdata.leasing_insurer_kpp
        }
      } else {
        return {
          leasing_term: '',
          leasing_advance_payment_rate: '',
          leasing_payment_schedule: '',
          leasing_asset_operation_territory: '',
          leasing_bank_account_number: '',
          leasing_corr_account_number: '',
          leasing_bank_name: '',
          leasing_bank_identification_code: '',
          leasing_holder_on_balance_name: '',
          leasing_holder_on_balance_ogrn: '',
          leasing_holder_on_balance_inn: '',
          leasing_holder_on_balance_kpp: '',
          leasing_insurer_name: '',
          leasing_insurer_ogrn: '',
          leasing_insurer_inn: '',
          leasing_insurer_kpp: ''
        }
      }
    }
  }
</script>
