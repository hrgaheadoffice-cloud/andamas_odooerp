/*
     Author => Albertus Restiyanto Pramayudha
     email  => xabre0010@gmail.com
     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
     youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
odoo.define('yudha_payment_voucher.add_antrian_payment', function (require) {
'use strict';

    var core = require('web.core');
    var Context = require('web.Context');
    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var AbstractView = require('web.AbstractView');
    var Widget = require('web.Widget');
    var session = require('web.session');
    var dialogs = require('web.view_dialogs');
    var dom = require('web.dom');
    var select_create_controllers_registry = require('web.select_create_controllers_registry');
    var SelectCreateListController = require('web._select_create_controllers_registry')
    var BasicController = require('web.BasicController');
    var AddQueueTreeButton = require('yudha_payment_voucher.tree_queuebutton');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var QWeb = core.qweb;
    var _t = core._t;

    var AntrianPaymentWidget = AbstractAction.extend({
        template: 'yudha_payment_voucher.buttons',
        events: {
            'change .oe_approval_model': 'onChangeApprovalMenu',
        },
        custom_events: {
            reload_record: function (event) {
                console.log('select record '+ $(event.data));
                this.onChangeApprovalMenu();
            },
        },
        init: function (parent, context, options) {
            this._super.apply(this, arguments);
            this._title = _t('Payment Plan Queue');
            this.model = false;
            this.domian = [];
            this.context = context;
            this.viewType = 'list';
        },

        start: async function() {
            await this._super(...arguments);
        },
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            this.isInDOM = true;
        },
        on_detach_callback: function () {
            this._super.apply(this, arguments);
            this.isInDOM = false;
        },
        onChangeApprovalMenu: async function () {
            var self = this;
            var targetMenu = this.$('.oe_approval_model option:selected').val();
            var viewRefID  = false;
            var user = session.uid
            if (targetMenu === 'vb_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'VendorBill'};
                this.domian = [['move_type','=','in_invoice'],['state','=','posted'],['already_process','=',false]];
            } else
            if (targetMenu === 'nois_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'NOI'};
                this.domian = [['is_noi_ho','=',true],['state','=','posted'],['already_process','=',false]];
            } else
            if (targetMenu === 'cashadvance_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'CA HO'};
                this.domian = [['ca_ho_id','!=',false],['state','=','posted'],['already_process','=',false]];
            } else
            if (targetMenu === 'settelement_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'Settlement HO'};
                this.domian = [['settelment_ho_id','!=',false],['state','=','posted'],['already_process','=',false]];
            } else
            if (targetMenu === 'cashrequest_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'Cash Request'};
                this.domian = [['cashrequest_id','!=',false],['state','=','posted'],['already_process','=',false]];
            } else
            if (targetMenu === 'reimbursement_payment'){
                this.model = 'account.move';
                this.context = {'model_name': 'Reimbursement HO'};
                this.domian = [['reimbursement_ho_id','!=',false],['state','=','posted'],['already_process','=',false]];
            }
            if (this.model !== false){
                return this.loadViews(this.model, false, [[viewRefID, this.viewType], [false, 'search']], {load_filters: true})
                    .then(this.setup.bind(self))
                    .then(function (fragment) {
                        self.$('.o_view_controller').remove()
                        dom.append(self.$('.o_contents'), [fragment], {
                            in_DOM: self.isInDOM,
                            callbacks: [{widget: self.viewController}],
                        });
//                        var MyButton = '<div role="toolbar" aria-label="Control panel buttons" class="o_cp_buttons"><div class="o_list_buttons" role="toolbar" aria-label="Main actions"><button class="btn btn-primary oe_add_to_queue"  type="button" accesskey="#">Add To Queue</button></div';
//                        var DivButton =self.$('.o_cp_top_left')
////                        DivButton.append(MyButton)
//                        var $button = dom.renderButton({
//                            attrs: {
//                                class: 'btn-primary',
//                                disabled: false,
//                            },
//                            text: 'Add To Queue',
//                        });
//                        $button.on('click', function (e) {
//                        console.log('this button click')
//                            var def;
//                            if (buttonData.click) {
//                                def = buttonData.click.call(self, e);
//                            }
//                            if (buttonData.close) {
//                                self.onForceClose = false;
//                                Promise.resolve(def).then(self.close.bind(self));
//                            }
//                        });
//                        DivButton.append($button)

                        return;
                    });
            }
        },

        setup: function (fieldsViews) {
            var self = this;
            var fragment = document.createDocumentFragment();
            var domain = self.domian;
            var ViewClass = ListView;
            var viewOptions = {};
            var selectCreateController;
            _.extend(viewOptions, {
                hasSelectors: true,
                readonly: false,
                hasButtons: true,
            });
            selectCreateController = AddQueueTreeButton;//select_create_controllers_registry.SelectCreateListController;
             var view = new ViewClass(fieldsViews[this.viewType], _.extend(viewOptions, {
                action: {
                    controlPanelFieldsView: fieldsViews.search,
                    help: _.str.sprintf("<p>%s</p>", _t("No records found!")),
                },
                action_buttons: false,
//                dynamicFilters: this.options.dynamicFilters,
                context: this.context,
                domain: domain,
                modelName: this.model,
                withBreadcrumbs: false,
                withSearchPanel: true,
            }));

            view.setController(AddQueueTreeButton);
            return view.getController(this).then(function (controller) {
                self.viewController = controller;
                return self.viewController.appendTo(fragment);
            }).then(function () {
                return fragment;
            });
        },

    });

    core.action_registry.add('yudha_antrian_payment', AntrianPaymentWidget);

    return AntrianPaymentWidget;
});