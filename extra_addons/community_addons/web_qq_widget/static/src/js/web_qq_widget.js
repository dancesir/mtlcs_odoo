/*---------------------------------------------------------
 * OpenERP QqWidget
 *---------------------------------------------------------*/
openerp.web_qq_widget = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.web.form.widgets.add('qq', 'instance.web_qq_widget.QqWidget');
    instance.web_qq_widget.QqWidget = instance.web.form.FieldChar.extend({
        display_name: _lt('QqWidget'),
        template: "QqWidget",
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                if (this.get('value')) {
                    this.$el.find('a').attr('href', 'http://wpa.qq.com/msgrd?v=3&uin=' + this.get('value') + '&site=qq&menu=yes').html('<button>开启QQ对话</button>');
                    this.$el.find(".qq_number").text(this.get('value'));
                }
                else{
                    this.$el.find('a').attr('href', '#').html('');
                    this.$el.find(".qq_number").text('');
                }
            }
        },
    });
};

// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
