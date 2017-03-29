openerp.web_nospace_fieldchar = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var FieldChar = instance.web.form.FieldChar
    FieldChar.include({
        parse_value: function (val, def) {
            if (this.$el.hasClass('field_char_not_space')) {
                val = val.replace(/\s+/g, "");
            }
            ;
            return instance.web.parse_value(val, this, def);
        },

    });

};