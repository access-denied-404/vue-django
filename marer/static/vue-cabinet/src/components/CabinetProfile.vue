<template>
  <div class="col-sm-9 col-md-10">

    <div class="panel panel-info">
        <div class="panel-heading">Профиль пользователя</div>
        <div class="panel-body">
            <form method="post">
                <div class="form-row">
                    <input type='hidden' name='csrfmiddlewaretoken' value='jt8x0IQD9aEt7PxV5H4m4bvk9EH2bfUQkfBNYuh2y0p8sTRObIYRinMeJeRl6fze' />
                    <div class="form-group col-md-6">
                        <label class="control-label" for="first_name">Имя</label>
                        <input type="text" name="profile-first_name" value="Владислав" id="id_profile-first_name" class="form-control" required />
                    </div>
                    <div class="form-group col-md-6">
                        <label class="control-label" for="last_name">Фамилия</label>
                        <input type="text" name="profile-last_name" value="Зиминов" id="id_profile-last_name" class="form-control" required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group col-md-12">
                        <label class="control-label" for="phone">Контактный телефон</label>
                        <input type="text" name="profile-phone" value="+7 (915) 245-78-25" id="id_profile-phone" class="form-control" required />
                    </div>
                </div>
                <button type="submit" class="btn btn-primary center-block">Сохранить изменения</button>
            </form>
        </div>
    </div>
    <div class="panel panel-info">
        <div class="panel-heading">Сменить пароль</div>
        <div class="panel-body">
            <form method="post">
                <div class="form-row">
                    <input type='hidden' name='csrfmiddlewaretoken' value='jt8x0IQD9aEt7PxV5H4m4bvk9EH2bfUQkfBNYuh2y0p8sTRObIYRinMeJeRl6fze' />
                    <div class="form-group col-md-12">
                        <label class="control-label" for="current_password">Старый пароль</label>
                        <input type="password" name="password-old_password" id="id_password-old_password" class="form-control" required />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group col-md-6">
                        <label class="control-label" for="new_password">Новый пароль</label>
                        <input type="password" name="password-password" id="id_password-password" class="form-control" required />
                    </div>
                    <div class="form-group col-md-6">
                        <label class="control-label" for="new_password_repeat">Пароль еще раз</label>
                        <input type="password" name="password-password_repeat" id="id_password-password_repeat" class="form-control" required />
                    </div>
                </div>


                <div class="row">
                    <div class="col-md-12">
                        <button type="submit" class="btn btn-primary center-block">Сохранить изменения</button>
                    </div>
                </div>
            </form>
        </div>
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
