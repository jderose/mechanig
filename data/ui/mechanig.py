#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Team:
#   J Phani Mahesh <phanimahesh@gmail.com> 
#   Barneedhar (jokerdino) <barneedhar@ubuntu.com> 
#   Amith KK <amithkumaran@gmail.com>
#   Georgi Karavasilev <motorslav@gmail.com>
#   Sam Tran <samvtran@gmail.com>
#   Sam Hewitt <hewittsamuel@gmail.com>
#
# Description:
#   A One-stop configuration tool for Unity.
#
# Legal Stuff:
#
# Mechanig is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# Mechanig is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/gpl-3.0.txt>

from gi.repository import Gtk,Gio,Gdk
import os
from ui import ui

class Mechanig ():
    def __init__(self):
        '''Handler Initialisations.
        Obtain all references here.'''
        self.builder = Gtk.Builder()
        self.glade="mechanig.glade"
# TODO : Use os module to resolve to the full path.
        self.builder.add_from_file(self.glade)
        self.ui=ui(self.builder)

# GSettings objects go here
        self.unityshell=self.plugin('unityshell')
        self.desktop=self.gnome('nautilus.desktop')
        self.background=self.gnome('desktop.background')
        self.launcher=self.unity('Launcher')
        self.power=self.canonical('indicator.power')

# Fire the engines
# The UI must be refreshed before connecting signals.
# Else all handlers get called when setting initial values and may cause a mess.
        self.refresh()
        self.builder.connect_signals(self)
        self.ui['mechanig_main'].set_resizable(False)
        self.ui['nb_mechanig'].set_show_tabs(False)
        self.ui['mechanig_main'].connect("delete-event", Gtk.main_quit)
        self.ui['mechanig_main'].show_all()
        Gtk.main()

#=====================================================================#
#                                Helpers                              #
#=====================================================================#
# TODO : Find better names.
    @staticmethod
    def resetAllKeys(schema,path=None):
        """Reset all keys in given Schema."""
        gsettings=Gio.Settings(schema=schema,path=path)
        for key in gsettings.list_keys():
            gsettings.reset(key)
    
    @staticmethod
    def color_to_hash(c):
        """Convert a Gdk.Color or Gdk.RGBA object to hex representation"""
        if isinstance(c,Gdk.Color):
            return "#{:02x}{:02x}{:02x}ff".format(*map(lambda x: round(x*255),[c.red_float,c.green_float,c.blue_float]))
        if isinstance(x,Gdk.RGBA):
            return "#{:02x}{:02x}{:02x}{:02x}".format(*map(lambda x: round(x*255),[c.red,c.green,c.blue,c.alpha]))
        # If it is neither a Gdk.Color object nor a Gdk.RGBA objcect,
        raise NotImplementedError

    def refresh(self):
        '''Reads the current config and refreshes the displayed values'''
    # Launcher
        dependants=['radio_reveal_left',
                    'radio_reveal_topleft',
                    'sc_reveal_sensitivity',
                    'l_launcher_reveal',
                    'l_launcher_reveal_sensitivity']
        if self.unityshell.get_int('launcher-hide-mode'):
            self.ui['sw_launcher_hidemode'].set_active(True)
            self.ui.sensitize(dependants)
        else:
            self.ui['sw_launcher_hidemode'].set_active(False)
            self.ui.unsensitize(dependants)
        del dependants
# Preferring readability over optimisations.
# I am aware of the redundancy and the better "[not] bool(value)"
        self.ui['radio_reveal_left'].set_active(True if self.unityshell.get_int('reveal-trigger') is 0 else False)
        self.ui['radio_reveal_topleft'].set_active(True if self.unityshell.get_int('reveal-trigger') is 1 else False)
        self.ui['sc_reveal_sensitivity'].set_value(self.unityshell.get_double('edge-responsiveness'))

        dependants=['l_launcher_transparency_scale',
                    'sc_launcher_transparency']
        opacity=self.unityshell.get_double('launcher-opacity')
        if opacity==1:
            self.ui['sw_launcher_transparent'].set_active(False)
            self.ui.unsensitize(dependants)
        else:
            self.ui['sw_launcher_transparent'].set_active(True)
            self.ui.sensitize(dependants)
        self.ui['sc_launcher_transparency'].set_value(opacity)
        del dependants
        del opacity

        mode = self.unityshell.get_int('num-launchers')
        self.ui['radio_launcher_visibility_all'].set_active(True if mode is 0 else False)
        self.ui['radio_launcher_visibility_primary'].set_active(True if mode is 1 else False)
        del mode

        color = self.unityshell.get_string('background-color')
        if color.endswith('00'):
            self.ui['radio_launcher_color_cham'].set_active(True)
            self.ui.unsensitize(['color_launcher_color_cus'])
        else:
            self.ui['radio_launcher_color_cus'].set_active(True)
            self.ui.sensitize(['color_launcher_color_cus'])
        valid,gdkcolor=Gdk.Color.parse(color[:-2])
        if valid:
            self.ui['color_launcher_color_cus'].set_color(gdkcolor)
        del color,valid,gdkcolor

        self.ui['spin_launcher_icon_size'].set_value(self.unityshell.get_int('icon-size'))

        self.ui['cbox_launcher_icon_colouring'].set_active(self.unityshell.get_int('backlight-mode'))

        self.ui['sw_launcher_show_desktop'].set_active(True if 'unity://desktop-icon' in self.launcher.get_strv('favorites') else False)
# TODO : Find a clever way or set each one manually.
# Do it the dumb way now. BIIIG refactoring needed later.

    @staticmethod
    def plugin(plugin):
        schema='org.compiz.'+plugin
        path='/org/compiz/profiles/unity/plugins/'+plugin+'/'
        return Gio.Settings(schema=schema,path=path)

    @staticmethod
    def unity(child=None):
        schema='com.canonical.Unity'
        schema=schema+'.'+child if child else schema
        return Gio.Settings(schema)

    @staticmethod
    def canonical(child):
        schema='com.canonical.'+child
        return Gio.Settings(schema)

    @staticmethod
    def compiz(child):
        schema='org.compiz.'+child
        return Gio.Settings(schema)

    @staticmethod
    def gnome(child):
        schema='org.gnome.'+child
        return Gio.Settings(schema)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\
# Dont trust glade to pass the objects properly.            |
# Always add required references to init and use them.      |
# That way, mechanig can resist glade stupidity.            |
# Apologies Gnome devs, but Glade is not our favorite.      |
#___________________________________________________________/

# ===== Top Navigation bar =====
    def on_tool_startpage_toggled(self,udata):
        self.ui['nb_mechanig'].set_current_page(0)
    def on_tool_unitysettings_toggled(self,udata):
        self.ui['nb_mechanig'].set_current_page(1)
        self.ui['nb_unitysettings'].set_current_page(0)
    def on_tool_compizsettings_toggled(self,udata):
        self.ui['nb_mechanig'].set_current_page(2)
        self.ui['nb_compizsettings'].set_current_page(0)
    def on_tool_themesettings_toggled(self,udata):
        self.ui['nb_mechanig'].set_current_page(3)
        self.ui['nb_themesettings'].set_current_page(0)
    def on_tool_desktopsettings_toggled(self,udata):
        self.ui['nb_mechanig'].set_current_page(4)
        
# ===== Start page =====
    # unity settings on start page 
    def on_tool_launcher_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(0)
    def on_tool_dash_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(1)
    def on_tool_panel_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(2)
    def on_tool_unity_switcher_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(3)    
    def on_tool_additional_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(4)    
    def on_tool_launcher_clicked(self,udata):
        self.ui['tool_unitysettings'].set_active(True)
        self.ui['nb_unitysettings'].set_current_page(0)
        
    # Compiz settings buttons on start page        
    def on_tool_general_clicked(self,udata):
        self.ui['tool_compizsettings'].set_active(True)
        self.ui['nb_compizsettings'].set_current_page(0)
    def on_tool_compiz_switcher_clicked(self,udata):
        self.ui['tool_compizsettings'].set_active(True)
        self.ui['nb_compizsettings'].set_current_page(1)
    def on_tool_windows_spread_clicked(self,udata):
        self.ui['tool_compizsettings'].set_active(True)
        self.ui['nb_compizsettings'].set_current_page(2)
    def on_tool_windows_snapping_clicked(self,udata):
        self.ui['tool_compizsettings'].set_active(True)
        self.ui['nb_compizsettings'].set_current_page(3)
    def on_tool_hotcorners_clicked(self,udata):
        self.ui['tool_compizsettings'].set_active(True)
        self.ui['nb_compizsettings'].set_current_page(4)
        
    # Theme settings on Start page    
    def on_tool_system_clicked(self,udata):
        self.ui['tool_themesettings'].set_active(True)
        self.ui['nb_themesettings'].set_current_page(0)  
    def on_tool_icons_clicked(self,udata):
        self.ui['tool_themesettings'].set_active(True)
        self.ui['nb_themesettings'].set_current_page(1) 
    def on_tool_cursors_clicked(self,udata):
        self.ui['tool_themesettings'].set_active(True)
        self.ui['nb_themesettings'].set_current_page(2)     
    def on_tool_fonts_clicked(self,udata):
        self.ui['tool_themesettings'].set_active(True)
        self.ui['nb_themesettings'].set_current_page(3)     
        
    # desktop settings on start page    
    def on_tool_desktop_clicked(self,udata): 
        self.ui['tool_desktopsettings'].set_active(True)

#===================END OF START PAGE===================#

#=====BEGIN: Unity settings=====
#-----BEGIN: Launcher ----------
    def on_sw_launcher_hidemode_active_notify(self,widget,udata=None):
        dependants=['radio_reveal_left',
                    'radio_reveal_topleft',
                    'sc_reveal_sensitivity',
                    'l_launcher_reveal',
                    'l_launcher_reveal_sensitivity']
        if self.ui['sw_launcher_hidemode'].get_active():
            self.unityshell.set_int("launcher-hide-mode",1)
            self.ui.sensitize(dependants)
        else:
            self.unityshell.set_int("launcher-hide-mode",0)
            self.ui.unsensitize(dependants)

    def on_radio_reveal_left_toggled(self,button,udata=None):
        radio=self.ui['radio_reveal_left']
        mode=0 if radio.get_active() else 1
        self.unityshell.set_int('reveal-trigger',mode)

# XXX :Strictly speaking, only one of these two will suffice.
    def on_radio_reveal_topleft_toggled(self,button,udata=None):
        radio=self.ui['radio_reveal_topleft']
        mode=0 if not radio.get_active() else 1
        self.unityshell.set_int('reveal-trigger',mode)

    def on_sc_reveal_sensitivity_value_changed(self,widget,udata=None):
        slider=self.ui['sc_reveal_sensitivity']
        val=slider.get_value()
        self.unityshell.set_double('edge-responsiveness',val)
# Two settings possible:
#        reveal-pressure (int,(1,1000))
#        edge-responsiveness (double,(0.2,8.0))
# XXX : To be discussed and changed if necessary.

    def on_sw_launcher_transparent_active_notify(self,widget,udata=None):
        dependants=['l_launcher_transparency_scale',
                    'sc_launcher_transparency']
        if self.ui['sw_launcher_transparent'].get_active():
            self.ui.sensitize(dependants)
            opacity=self.ui['sc_launcher_transparency'].get_value()
            self.unityshell.set_double('launcher-opacity',opacity)
        else:
            self.ui.unsensitize(dependants)
            self.unityshell.set_double('launcher-opacity',1)
# Check adj_launcher_transparency if this misbehaves

    def on_sc_launcher_transparency_value_changed(self,widget,udata=None):
        opacity=self.ui['sc_launcher_transparency'].get_value()
        self.unityshell.set_double('launcher-opacity',opacity)
# Check adj_launcher_transparency if this misbehaves
        
    def on_radio_launcher_visibility_all_toggled(self,widget,udata=None):
        if self.ui['radio_launcher_visibility_all'].get_active():
            self.unityshell.set_int('num-launchers',0)
        else:
            self.unityshell.set_int('num-launchers',1)

    def on_radio_launcher_color_cus_toggled(self,widget,udata=None):
        dependants=['color_launcher_color_cus']
        color=self.ui['color_launcher_color_cus'].get_color()
        colorhash=self.color_to_hash(color)
        if self.ui['radio_launcher_color_cus'].get_active():
            self.ui.sensitize(dependants)
            self.unityshell.set_string('background-color',colorhash)
        else:
            self.ui.unsensitize(dependants)
            self.unityshell.set_string('background-color',colorhash[:-2]+'00')

    def on_color_launcher_color_cus_color_set(self,widget,udata=None):
        color=self.ui['color_launcher_color_cus'].get_color()
        colorhash=self.color_to_hash(color)
        self.unityshell.set_string('background-color',colorhash)

    def on_spin_launcher_icon_size_value_changed(self,widget,udata=None):
        size=self.ui['spin_launcher_icon_size'].get_value()
        self.unityshell.set_int('icon-size',size)

    def on_cbox_launcher_icon_colouring_changed(self,widget,udata=None):
        mode=self.ui['cbox_launcher_icon_colouring'].get_active()
        self.unityshell.set_int('backlight-mode',mode)
    
    def on_sw_launcher_show_desktop_active_notify(self,widget,udata=None):
        fav=self.launcher.get_strv('favorites')
        desktop="unity://desktop-icon"
        if self.ui['sw_launcher_show_desktop'].get_active():
            if desktop not in fav:
                fav.append(desktop)
                self.launcher.set_strv('favorites',fav)
        else:
            if desktop in fav:
                fav.remove(desktop)
                self.launcher.set_strv('favorites',fav)

# TODO : RESET handler
# ---------- END Launcher -------

# ---------- BEGIN DASH

    def on_sw_dash_blur_active_notify(self,widget,udata=None):
        dependants=['radio_dash_blur_smart',
                    'radio_dash_blur_static',
                    'l_dash_blur']
        
        if self.ui['sw_dash_blur'].get_active():
            self.ui.sensitize(dependants)
            self.unityshell.set_int('dash-blur-experimental',1)
            
        else:
            self.ui.unsensitize(dependants)
            self.unityshell.set_int('dash-blur-experimental',0)
    
    def on_radio_dash_blur_smart_toggled(self,button,udata=None):
        mode=1 if button.get_active() else 2
        self.unityshell.set_int('dash-blur-experimental',mode)
     
      # selective selection in unity-dash - part 2
      
    def on_radio_dash_color_cus_active_notify(self,widget,udata=None):
        dependants=['color_dash_color_cus']
        
        if self.ui['radio_dash_color_cus'].get_active():
            self.ui.sensitize(dependants)
        else:
            self.ui.unsensitize(dependants)

    
#-----BEGIN: Panel -----            
  
    def on_sw_appmenu_autohide_active_notify(self,widget,udata=None):
        dependants=['spin_menu_visible','l_menu_visible']
        
        if widget.get_active():
            self.ui.sensitize(dependants)
                    
        else:
            self.ui.unsensitize(dependants)
            
    # selective selection in unity-panel  part 2
  
    def on_sw_transparent_panel_active_notify(self,widget,udata=None):
        dependants=['sc_panel_transparency','l_transparent_panel','check_panel_opaque']

        if widget.get_active():
            self.ui.sensitize(dependants)
           
        else:
            self.ui.unsensitize(dependants)
            self.unityshell.set_double('panel-opacity',1.00)
            self.ui['sc_panel_transparency'].set_value(1.00)

    def on_sc_panel_transparency_value_changed(self,widget,udata=None):
        panel_transparency=widget.get_value()
        self.unityshell.set_double('panel-opacity',panel_transparency)        

    def on_check_panel_opaque_toggled(self,widget,udata=None):

        if widget.get_active():
            self.unityshell.set_boolean('panel-opacity-maximized-toggle',True)
        else:
            self.unityshell.set_boolean('panel-opacity-maximized-toggle',False)


    def on_check_indicator_username_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.unityshell.set_boolean('',)


    def on_check_indicator_batterytime_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.power.set_boolean('show-time',True)
        else:
            self.power.set_boolean('show-time',False)
            

#-----BEGIN: Switcher-----

    def on_check_switchwindows_all_workspaces_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.unityshell.set_boolean()
    
        else:
            self.unityshell.set_boolean()    
    
    
    def on_check_switcher_showdesktop_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.unityshell.set_boolean("disable-show-desktop",False)
        
        else:
            self.unityshell.set_boolean("disable-show-desktop",True)        
        
    def on_check_minimizedwindows_switch_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.unityshell.set_boolean("show-minimized-windows",True)
            
        else:
            self.unityshell.set_boolean("show-minimized-windows",False)
    
    def on_check_autoexposewindows_toggled(self,widget,udata=None):
    
        if widget.get_active():
            self.unityshell.set_boolean()
            
        else:
            self.unityshell.set_boolean()
            
    # keyboard widgets in unity-windows-switcher

    def on_craccel_unity_switcher_windows_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_unity_switcher_windows_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_unity_switcher_windows_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_unity_switcher_windows_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")

    # keyboard widgets in unity-launcher-switcher

    def on_craccel_unity_switcher_launcher_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_unity_switcher_launcher_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_unity_switcher_launcher_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_unity_switcher_launcher_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")

  
#-----BEGIN: Additional -----

    def on_check_shortcuts_hints_overlay_toggled(self,widget,udata=None):
        
        if widget.get_active():
            self.unityshell.set_boolean('shortcut-overlay',True)
        
        else:
            self.unityshell.set_boolean('shortcut-overlay',False)
            
            
    # keyboard widgets in unity-additional

    def on_craccel_unity_additional_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        # Glade has a habit of swapping arguments. beware.
        model=self.ui['list_unity_additional_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_unity_additional_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_unity_additional_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")
            
#=====BEGIN: Compiz settings=====
#-----BEGIN: General -----
            
     # selective sensitivity in compiz - general
            
    def on_sw_compiz_zoom_active_notify(self,widget,udata=None):
        dependants=['radio_zoom_type_standard','radio_zoom_type_lg','l_compiz_zoom_type']
        
        if widget.get_active():
            self.ui.sensitize(dependants)
           
        else:
            self.ui.unsensitize(dependants)
            


    # keyboard widgets in compiz-general-zoom

    def on_craccel_compiz_general_zoom_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_compiz_general_zoom_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)
    def on_craccel_compiz_general_zoom_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_compiz_general_zoom_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")

    # keyboard widgets in compiz-general-keys

    def on_craccel_compiz_general_keys_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_compiz_general_keys_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_compiz_general_keys_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_compiz_general_keys_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")
            
#-----BEGIN: Workspaces -----
           
    # selective sensitivity in compiz - workspaces
    
    def on_sw_workspace_switcher_active_notify(self,widget,udata=None):
        dependants=['l_horizontal_desktop','l_vertical_desktop','spin_horizontal_desktop','spin_vertical_desktop']

        if widget.get_active():
            self.ui.sensitize(dependants)
           
        else:
            self.ui.unsensitize(dependants)
            

    # keyboard widgets in compiz-workspace

    def on_craccel_compiz_workspace_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_compiz_workspace_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_compiz_workspace_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_compiz_workspace_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")
        
        
    # compiz hotcorner linked button 
    def on_lb_configure_hot_corner_activate_link(self,udata):
        self.ui['nb_compizsettings'].set_current_page(4)
    

        


#-----BEGIN: Windows Spread -----

    # selective sensitivity in compiz - windows spread
    
    def on_sw_windows_spread_active_notify(self,widget,udata=None):
        dependants=['l_compiz_spacing','spin_compiz_spacing','check_overlay_emblem','check_click_desktop']

        if widget.get_active():
            self.ui.sensitize(dependants)
           
        else:
            self.ui.unsensitize(dependants)
 

    # keyboard widgets in compiz-windows-spread

    def on_craccel_compiz_windows_spread_accel_edited(self,craccel, path, key, mods, hwcode,model=None):
        model=self.ui['list_compiz_windows_spread_accelerators']
        accel = Gtk.accelerator_name(key, mods)
        iter = model.get_iter(path)
        model.set_value(iter, 1, accel)

    def on_craccel_compiz_windows_spread_accel_cleared(self, craccel, path, model=None):
        model=self.ui['list_compiz_windows_spread_accelerators']
        iter = model.get_iter(path)
        model.set_value(iter, 1, "Disabled")
            
 
    # compiz hotcorner linked button
    
    def on_lb_configure_hot_corner_windows_spread_activate_link(self,udata):
        self.ui['nb_compizsettings'].set_current_page(4)

            
             
#========= Begin Desktop Settings
    def on_sw_desktop_icon_active_notify(self,widget,udata=None):
        dependants=['l_desktop_icons_display','check_desktop_home','check_desktop_networkserver','check_desktop_trash','check_desktop_devices']
        
        if widget.get_active():
            self.background.set_boolean("show-desktop-icons",True)
            self.ui.sensitize(dependants)
           
        else:
            self.ui.unsensitize(dependants)
            self.background.set_boolean("show-desktop-icons",False)
    
    def on_check_desktop_home_toggled(self,widget,udata=None):
        self.desktop.set_boolean('home-icon-visible',
                                 self.ui['check_desktop_home'].get_active())

    def on_check_desktop_networkserver_toggled(self,widget,udata=None):
        self.desktop.set_boolean('network-icon-visible',
                            self.ui['check_desktop_networkserver'].get_active())

    def on_check_desktop_trash_toggled(self,widget,udata=None):
        self.desktop.set_boolean('trash-icon-visible',
                            self.ui['check_desktop_trash'].get_active())

    def on_check_desktop_devices_toggled(self,widget,udata=None):
        self.desktop.set_boolean('volumes-visible',
                            self.ui['check_desktop_devices'].get_active())

    def on_spin_iconsize_value_changed(self,udata=None):
        size=self.ui['spin_iconsize'].get_value()
# TODO : Find where this setting is.

    def on_check_alignment_toggled(self,widget,udata=None):
        pass
# TODO : Find where this setting is.


#-----END OF CONFIGURATIONS-----
             
    # gtk search box
    
    # inserting text shows the secondary icon (stock-clear)
    
    def on_tool_entry_search_insert_text(self,text,length,position,udata):
    
        # getting the text length to workaround some Gtk bug
        if self.ui['tool_entry_search'].get_text_length()+1:
            self.ui['tool_entry_search'].set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY,
                Gtk.STOCK_CLEAR)
            
        else:
            self.ui['tool_entry_search'].set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None) 

    def on_tool_entry_search_delete_text(self,start_pos,end_pos,udata):
       
        # getting the text length to workaround some Gtk bug        
        
        if (self.ui['tool_entry_search'].get_text_length()-1) == 0:
            self.ui['tool_entry_search'].set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)
            
    # clicking on secondary icon clearing text
     
    def on_tool_entry_search_icon_press(self, widget, icon, mouse_button):
         
        if icon == Gtk.EntryIconPosition.SECONDARY:
            widget.set_text("")
            widget.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)
            
        if icon == Gtk.EntryIconPosition.PRIMARY:
            print("Searching")


if __name__=='__main__':
# Fire up the Engines
    Mechanig()
else:
    print("WARNING: This module is not tailored to be imported. Proceed at your own risk.")
