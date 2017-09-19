<template>
  <div id="app-root">
    <form method="post">
      <div class="panel panel-primary">
        <div class="panel-heading">Оформление заявки</div>
        <div class="panel-body">
          <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">
          <div class="row">
            <div class="col-md-6">
              <bs3-select-field
                v-model="product"
                :name="'product'"
                :label="'Тип заявки'"
                :options="products"
              ></bs3-select-field>
            </div>
            <div class="col-md-6">
              <bs-input
                :name="'org_name'"
                label="Организация"
                v-model="org_search_name"
              ></bs-input>
            </div>
          </div>
        </div>
      </div>
      <transition appear name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
      <button type="submit" class="btn btn-primary center-block">Сохранить</button>
    </form>
  </div>
</template>

<script>
  import {input} from 'vue-strap'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  export default {
    name: 'app',
    props: ['csrf', 'products'],
    components: {
      'bs-input': input,
      'bs3-select-field': BS3SelectField
    },
    data () {
      return {
        product: document.getElementById('app').getAttribute('product'),
        org_search_name: ''
      }
    },
    watch: {
      product (e) {
        window.location.hash = '/' + this.product
      }
    },
    created () {
      window.location.hash = '/' + this.product
    }
  }
</script>

<style scoped>
  label {
    text-align: left;
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .5s ease;
  }

  .fade-enter, .fade-leave-active {
    opacity: 0
  }
</style>
