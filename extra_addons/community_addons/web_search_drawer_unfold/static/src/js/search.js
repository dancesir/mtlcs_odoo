openerp.web_search_drawer_unfold = function(instance) {

	instance.web.SearchView.include({

	    start: function() {
	    	var self = this;
	    	var p = {};
	        this.$view_manager_header = this.$el.parents(".oe_view_manager_header").first();
	        this.setup_global_completion();
	        this.query = new instance.web.search.SearchQuery()
	                .on('add change reset remove', this.proxy('do_search'))
	                .on('change', this.proxy('renderChangedFacets'))
	                .on('add reset remove', this.proxy('renderFacets'));

	        if (this.options.hidden) {
	            this.$el.hide();
	        }
	        if (this.headless) {
	            this.ready.resolve();
	        } else {
	            var load_view = instance.web.fields_view_get({
	                model: this.dataset._model,
	                view_id: this.view_id,
	                view_type: 'search',
	                context: this.dataset.get_context(),
	            });

	            this.alive($.when(load_view)).then(function (r) {
	                self.fields_view_get.resolve(r);
	                return self.search_view_loaded(r);
	            }).fail(function () {
	                self.ready.reject.apply(null, arguments);
	            });
	        }

	        var view_manager = this.getParent();
	        while (!(view_manager instanceof instance.web.ViewManager) &&
	                view_manager && view_manager.getParent) {
	            view_manager = view_manager.getParent();
	        }

	        if (view_manager) {
	            this.view_manager = view_manager;
	            view_manager.on('switch_mode', this, function (e) {
	                self.drawer.toggle(e !== 'form');
	            });
	        }
	        return $.when(p, this.ready);
	    },
	});

};