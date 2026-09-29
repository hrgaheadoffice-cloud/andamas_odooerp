odoo.define('yudha_dashboard_approval.approval_menu', function (require) {
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
    var ListView = require('web.ListView');
    var ListController = require('web.ListController');
    var ListRenderer = require('web.ListRenderer');
    var FormView = require('web.FormView');
    var FormController = require('web.FormController');
    var KanbanView = require('web.KanbanView');
    var ServiceProviderMixin = require('web.ServiceProviderMixin');
    var select_create_controllers_registry = require('web.select_create_controllers_registry');
    var SelectCreateListController = require('web._select_create_controllers_registry')
    var BasicController = require('web.BasicController');
    var QWeb = core.qweb;
    var _t = core._t;

    var SelectCreateListControllers = ListController.extend({
        _onOpenRecord: function (ev) {
            ev.stopPropagation();
            var self = this;
            var record = this.model.get(ev.data.id, {raw: true});
            console.log('rec',ev)
            new dialogs.FormViewDialog(self, {
                context: ev.data.context,
                fields_view: ev.data.fields_view,
                on_saved: ev.data.on_saved,
                on_remove: ev.data.on_remove,
                readonly: true,
                deletable: false,
                res_id: record.res_id,
                res_model: record.model,
                title: _t("Open: ") + ev.data.string,
            }).open();
        },
    });

    ListController.include({
        _getActionMenuItems: function (state) {
            let values = this._super.apply(this, arguments);
            if (!this.hasActionMenus || !this.selectedRecords.length) {
                return values;
            }

            const models = ['account.move', 'purchase.request', 'purchase.order', 'cash.advance.ho', 'cash.advance.site',
            'cash.request', 'reimbursement.site', 'reimbursement.ho', 'sundry', 'noi', 'settelment.site', 'settelment.ho'];
            if (models.includes(this.modelName)) {
                values.items.other.push({
                    description: _t("Approval"),
                    callback: () => {
                        Dialog.confirm(this, _t("Are you sure that you want to Approved all the selected records?"), {
                            confirm_callback: () => this._toggleApprovalRecord(),
                        });
                    }
                });
            }
            return values;

        },
        _toggleApprovalRecord: async function () {
            var self = this;
            const resIds = await this.getSelectedIdsWithDomain()
            const notif = this.isDomainSelected;
            var domain;
            if (resIds.length >1){
                domain=[['id','in',resIds]]
            } else{
               domain=[['id','in',resIds]]
            }
            var def = this._rpc({
                        model: this.modelName,
                        method: 'search_read',
                        domain: domain,
                        fields: ['state'],
                    }).then(function (result) {
                        for(var j=0; j<= result.length; j++){
                            if (result[j] !== undefined){
                                if(self.modelName  ==='purchase.request'){
                                    if(result[j]['state'] =='to_approve'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_approved',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else if(result[j]['state'] =='to_approve1'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_approved1',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else if(result[j]['state'] =='to_approve2'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_approved2',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else
                                    if(result[j]['state'] =='to_approve3'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_approved3',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else if(result[j]['state'] =='to_approve4'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_approved4',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    }
                                } else
                                  if(self.modelName  ==='purchase.order'){
                                    if(result[j]['state'] =='approved1'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_appr1',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else
                                    if(result[j]['state'] =='approved2'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_appr2',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else
                                    if(result[j]['state'] =='approved3'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_appr3',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else
                                    if(result[j]['state'] =='approved4'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_appr4',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    } else
                                    if(result[j]['state'] =='approved5'){
                                       self._rpc({
                                            model: self.modelName,
                                            method: 'button_appr5',
                                            args: [[result[j]['id']]],
                                       }).then(function () {
                                            self.trigger_up('reload_record', {});
                                       });
                                    }
                                }
                            }

                        }

                    });
        },
    });

    var approvalMenuWidget = AbstractAction.extend({
        template: 'yudha_dashboard_approval.buttons',
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
            this._title = _t('Approval Menu');
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
            if (targetMenu === 'pr_approval'){
                this.model = 'purchase.request';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'po_approval'){
                this.model = 'purchase.order';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'vb_approval'){
                this.model = 'account.move';
                this.domian = [['move_type','=','in_invoice']];
            } else if (targetMenu === 'ci_approval'){
                this.model ='account.move';
                this.domian = [['move_type','=','out_invoice']];
            } else if (targetMenu === 'cashadvance_approval'){
                this.model ='cash.advance.ho';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'cashadvance_approval_site'){
                this.model ='cash.advance.site';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'settlement_approval'){
                this.model ='settelment.ho';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'settlement_approval_site'){
                this.model ='settelment.site';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'cashrequest_approval'){
                this.model ='cash.request';
                this.domian = [['next_approver','=',user]];
            } else if (targetMenu === 'reimbursement_approval'){
                this.model ='reimbursement.ho';
                this.domian = [];
            } else if (targetMenu === 'reimbursement_approval_site'){
                this.model ='reimbursement.site';
                this.domian = [];
            } else if (targetMenu === 'sundry_approval'){
                this.model ='account.move';
                this.domian = [['is_sundry','=',true]];
            } else if (targetMenu === 'sundry_site_approval'){
                this.model ='sundry';
                this.domian = [];
            } else if (targetMenu === 'noi_approval'){
                this.model ='noi';
                this.domian = [];
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
            });
            selectCreateController = SelectCreateListControllers;
             var view = new ViewClass(fieldsViews[this.viewType], _.extend(viewOptions, {
                action: {
                    controlPanelFieldsView: fieldsViews.search,
                    help: _.str.sprintf("<p>%s</p>", _t("No records found!")),
                },
                action_buttons: false,
//                dynamicFilters: this.options.dynamicFilters,
//                context: this.context,
                domain: domain,
                modelName: this.model,
                withBreadcrumbs: false,
                withSearchPanel: false,
            }));
            view.setController(selectCreateController);
            return view.getController(this).then(function (controller) {
                self.viewController = controller;
                return self.viewController.appendTo(fragment);
            }).then(function () {
                return fragment;
            });
        },

    });

    core.action_registry.add('yudha_approval_menu', approvalMenuWidget);

    return approvalMenuWidget;
});