
console.info('ddd');

openerp.dynamic_list = function (instance) {

    ListView = instance.web.ListView;

    console.info('ddd2');

    ListView.include({

		init: function(parent, dataset, view_id, options) {
			var self = this;
			this._super.apply(this, arguments);
            console.info('ddd2');
	    },


        start: function() {
            console.info('ddd3');
            return this._super();
        },

        reload: function () {
            this.setup_columns(this.fields_view.fields, this.grouped);
            this.$el.html(QWeb.render(this._template, this));
            return this.reload_content();
        },

    })

};


console.info('ddd999');

