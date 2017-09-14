<template>
  <div id="app-root">
    <div class="panel panel-primary">
      <div class="panel-heading">Оформление заявки</div>
      <div class="panel-body">

        <form method="post">

          <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">

          <div class="form-row">
            <div class="col-md-12">
              <bs3-select-field
                v-model="product"
                :name="'product'"
                :label="'Тип заявки'"
                :options="products"
              ></bs3-select-field>
            </div>
          </div>

          <transition appear name="fade" mode="out-in">
            <router-view></router-view>
          </transition>

          <button type="submit" class="btn btn-primary center-block">Сохранить</button>
        </form>

      </div>
    </div>
  </div>
</template>

<script>
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  export default {
    name: 'app',
    props: ['csrf', 'products'],
    components: {
      'bs3-select-field': BS3SelectField
    },
    data () {
      return {
        product: window.location.hash.substr(2)
      }
    },
    watch: {
      product (e) {
        window.location.hash = '/' + this.product
      }
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
