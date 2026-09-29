odoo.define('nieve_direct_query.dquery_summary', function(require) {

    var core = require('web.core');
    var data = require('web.data');
    var ActionManager = require('web.ActionManager');
    var form_common = require('web.form_common');
    var time = require('web.time');
    var _t = core._t;
    var QWeb = core.qweb;

    var DirectQuery = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
        display_name: _t('Form'),
        // view_type: "form",
        init: function() {
            this._super.apply(this, arguments);
            if (this.field_manager.model == "ms.query") {
                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
            this.set({
                summary_header: false,
                room_summary: false,
            });
            this.summary_header = [];
            this.room_summary = [];
            this.field_manager.on("field_changed:summary_header", this, function() {
                this.set({ "summary_header": this.field_manager.get_field_value("summary_header") });
            });
            this.field_manager.on("field_changed:room_summary", this, function() {
                this.set({ "room_summary": this.field_manager.get_field_value("room_summary") });
            });
        },

        initialize_field: function() {

            form_common.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:summary_header", self, self.initialize_content);
            self.on("change:room_summary", self, self.initialize_content);
        },

        initialize_content: function() {
            var self = this;
            if (self.setting)
                return;

            if (!this.summary_header || !this.room_summary)
                return
                // don't render anything until we have summary_header and room_summary

            this.destroy_content();

            if (this.get("summary_header")) {
                this.summary_header = py.eval(this.get("summary_header"));
            }
            if (this.get("room_summary")) {
                this.room_summary = py.eval(this.get("room_summary"));
            }

            this.renderElement();
            this.view_loading();
        },

        view_loading: function(r) {
            return this.load_form(r);
        },

        load_form: function(data) {
            self.action_manager = new ActionManager(self);

        },

        renderElement: function() {
            this.destroy_content();
            this.$el.html(QWeb.render("DirectQueryShow", { widget: this }));
        }
    });
    core.form_custom_registry.add('dquery_summary', DirectQuery);
});