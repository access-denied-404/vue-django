<template>
  <div class="col-sm-9 col-md-10">
    <div class="pull-right">
      <form class="form-inline">
        <div class="form-group">
          <label>Статус заявки</label>
          <select name="status" id="id_status" class="form-control">
            <option value="" selected>Все</option>
            <option value="registering">Оформление заявки</option>
            <option value="review">Рассмотрение заявки</option>
            <option value="finished">Завершена</option>
            <option value="cancelled">Отменена</option>
            <option value="client_revision">Отправлено клиенту на доработку</option>
            <option value="returned_from_revision">Возвращена с доработки</option>
            <option value="client_agreement">Отправлено на согласование клиенту</option>
            <option value="cancelled_by_client">Отменена клиентом</option>
          </select>
        </div>
      </form>
    </div>
    <div class="clearfix"></div>
    <br/>
    <div class="panel panel-info">
      <table class="table">
        <tbody>
          <tr class="bg-info">
            <th class="h6">
              Номер
              <small><a href="?order_by=-id"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=id"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th class="h6">
              Дата<br/>заведения<br/>заявки
              <small><a href="?order_by=-created_at"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=created_at"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th class="h6">
              Организация
              <small><a href="?order_by=-issuer_full_name"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=issuer_full_name"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th class="h6">
              Сумма
              <small><a href="?order_by=-bg_sum"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=bg_sum"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th class="h6">
              Статус
              <small><a href="?order_by=-status"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=status"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th class="h6">
              Последний<br/>комментарий
              <small><a href="?order_by=-comment"><p class="glyphicon glyphicon-arrow-up fs-10"></p></a></small>
              <small><a href="?order_by=comment"><p class="glyphicon glyphicon-arrow-down fs-10"></p></a></small>
            </th>
            <th></th>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'issues',
    data () {
      return {
      }
    }
  }
</script>
