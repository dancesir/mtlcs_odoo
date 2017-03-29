openerp.create_and_edit_many2one = function(instance) {
    var _t = instance.web._t,
   _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.Session.include({
        session_init: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function(res) {
                if (self.session_is_valid()) {
                    self.rpc('/create_and_edit_many2one/create_edit_allowed', {}).then(function(result) {
                        self.no_create_edit = result;
                    });
                    return res;
                }
            });
        }
    });
    
    instance.web.form.SelectCreatePopup.include({
        setup_search_view: function(search_defaults) {
            var self = this;
            super_res = this._super.apply(this, arguments);
            if (!this.session.no_create_edit) {
                return super_res;
            }else{
                this.searchview.on("search_view_loaded", self, function() {
                    self.view_list.on("list_view_loaded", self, function() {
                        var $cbutton = self.$buttonpane.find(".oe_selectcreatepopup-search-create");
                        $cbutton.attr("disabled", "disabled");
                    });
                });
            }
        }
    });
    
    instance.web.form.FieldMany2One.include({
        init: function() {
            this._super.apply(this, arguments);
        },
        evict_create_edit: function(values) {
            for (i=0; i<values.length; ++i) {
                console.log(values[i].label);
                if(values[i].label == _t("Create and Edit...")) {
                    values.splice(i, 1);                    
                    //values.splice(values.length-1, 1);
                }                
                else if(values[i].label.indexOf(_t('Create')) != -1){
                    values.splice(i, 2);  
                }
            }
            return values
        },
        get_search_result: function(search_val) {
            var self = this;
            super_res = this._super.apply(this, arguments);
            if (!this.session.no_create_edit) {
                return super_res;
            } else {
                return super_res.then(function(values) {
                    values = self.evict_create_edit(values)
                    return $.Deferred().resolve(values);
                });
            }
        },
        show_error_displayer: function() {
            var self = this;
            if (!this.session.no_create_edit) {
                super_res = this._super.apply(this, arguments);
            }
        },
    });
};