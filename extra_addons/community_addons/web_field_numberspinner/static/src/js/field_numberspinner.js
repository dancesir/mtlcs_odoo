/******************************************************************************
******************************************************************************/

openerp.web_field_numberspinner = function (instance){
    /***************************************************************************
    Create an new 'NumberSpinnerWidget' widget that allow users to adjust number easy
    ***************************************************************************/

    instance.web.form.NumberSpinnerWidget = instance.web.form.FieldFloat.extend({
        template: 'NumberSpinnerWidget',
        init: function() {
            this._super.apply(this, arguments);

        },

        start: function() {
            var tmp = this._super();
            return tmp;
        },

    });

    instance.web.form.widgets = instance.web.form.widgets.extend({
        'numberspinner' : 'instance.web.form.NumberSpinnerWidget'
    });

    //instance.web_view_editor.ViewEditor.FieldFloat = instance.web_view_editor.ViewEditor.FieldChar.extend({
    //});




};



