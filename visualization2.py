from utils import *
from warehouse_map import *
from robot_fleet import *
import plotly.graph_objects as go

class Visualizer:
    colors = ['rgba( 31,  119, 180, 1.0 )', 
              'rgba(255, 127,   14, 1.0 )',
              'rgba( 44, 160,   44, 1.0 )', 
              'rgba(214,  39,   40, 1.0 )',
              'rgba(148, 103,  189, 1.0 )', 
              'rgba(140,  86,   75, 1.0 )',
              'rgba(227, 119,  194, 1.0 )', 
              'rgba(127, 127,  127, 1.0 )',
              'rgba(188, 189,   34, 1.0 )', 
              'rgba( 23, 190,  207, 1.0 )']
    def __init__(self, wh_map, task_list, fleet, vis_type="default_static", show_t=True, tasks_colored=True, task_plotter="fleet"):
        self.wh_map = wh_map
        self.fleet = fleet
        self.task_list = task_list
        self.show_t = show_t

        type_options = {
            "default_static": self.color_tasks_traces_off,
            "color_tasks_traces_off": self.color_tasks_traces_off,
            "black_tasks_traces_on": self.black_tasks_traces_on,
            "fleet_tasks": self.fleet_tasks
        }
        self.vis_func = type_options[vis_type]

        self.fig = go.Figure()
        self.set_fig_layout()

    # def __repr__(self):
    #     pass

    def show(self):
        self.vis_func()
        self.fig.show()

    def color_tasks_traces_off(self):
        self.plot_blocked_areas()
        self.plot_tasks()

    def black_tasks_traces_on(self):
        self.plot_blocked_areas()
        self.plot_tasks(color="rgba(10,10,10,0.4)")
        self.trace_robot_paths(show_t=self.show_t)
        
    def fleet_tasks(self):
        self.plot_blocked_areas()
        robots = self.fleet.get_robots_as_list()
        for robot in robots:
            self.plot_tasks(tasks=robot.task_list.tasks)

    def set_fig_layout(self):
        self.fig.update_layout(
            scene = dict(
                xaxis = dict(nticks=self.wh_map.wh_zone.x_range()//5, range=[self.wh_map.wh_zone.x_lims[1], self.wh_map.wh_zone.x_lims[0]]),
                yaxis = dict(nticks=self.wh_map.wh_zone.y_range()//5, range=self.wh_map.wh_zone.y_lims,),
                zaxis = dict(nticks=self.wh_map.wh_zone.z_range()//5, range=self.wh_map.wh_zone.z_lims,),
                aspectmode="data"),
            width=1500,
            margin=dict(r=20, l=20, b=20, t=20))
    
    def color(self, idx):
        return self.colors[idx % len(self.colors)]
    
    def make_zone_mesh(self, zone, color="red", name="", hoverinfo=None):
        x, y, z, i, j, k = zone.mesh_params()
        if hoverinfo == None:
            return go.Mesh3d(x=x, y=y, z=z, i = i, j = j, k = k, opacity=0.4, color=color, flatshading = True, name=name)
        else:
            return go.Mesh3d(x=x, y=y, z=z, i = i, j = j, k = k, opacity=0.4, color=color, flatshading = True, name=name, hoverinfo=hoverinfo)
    
    def plot_blocked_areas(self, hoverinfo="skip"):
        lightness = 150
        color = f'rgb({lightness},{lightness},{lightness})'
        for blocked_area in self.wh_map.blocked_areas:
            self.fig.add_trace(self.make_zone_mesh(blocked_area, hoverinfo="skip", color=color))
            
    

    def plot_tasks(self, tasks=None, color=None):
        """Plots task pick and drop locations"""
        if tasks == None:
            tasks = self.task_list.tasks
        if color == None:
            for i in range(len(tasks)):
                task_num = int(tasks[i].task_id[1:])
                marker_size = np.linspace(10,5, len(tasks))
                pick_str = tasks[i].pick_point.as_str()
                drop_str = tasks[i].drop_point().as_str()
                self.fig.add_scatter3d(
                    x=[tasks[i].pick_point.x,tasks[i].drop_point().x], 
                    y=[tasks[i].pick_point.y,tasks[i].drop_point().y], 
                    z=[tasks[i].pick_point.z,tasks[i].drop_point().z], 
                    mode='lines',
                    marker=dict(color=self.color(task_num)), 
                    name=f"Task {tasks[i].task_id}")
                self.fig.add_scatter3d(
                    x=[tasks[i].pick_point.x], 
                    y=[tasks[i].pick_point.y], 
                    z=[tasks[i].pick_point.z], 
                    mode='markers+text',
                    marker=dict(color=self.color(task_num), size=marker_size[i]),
                    name=f"Pick {tasks[i].task_id}: {pick_str}",
                    text=[tasks[i].task_id])
                self.fig.add_scatter3d(
                    x=[tasks[i].drop_point().x], 
                    y=[tasks[i].drop_point().y], 
                    z=[tasks[i].drop_point().z], 
                    mode='markers',
                    marker=dict(color=self.color(task_num), size=marker_size[i],
                                symbol='square'), 
                    name=f"Drop {tasks[i].task_id}: {drop_str}")
        else:
            marker_size = 10
            for i in range(len(tasks)):
                pick_str = tasks[i].pick_point.as_str()
                self.fig.add_scatter3d(
                    x=[tasks[i].pick_point.x,tasks[i].drop_point().x], 
                    y=[tasks[i].pick_point.y,tasks[i].drop_point().y], 
                    z=[tasks[i].pick_point.z,tasks[i].drop_point().z], 
                    mode='lines+markers',
                    marker=dict(color=color, size=marker_size, symbol='square'),
                    name=f"Task {tasks[i].task_id}")
                self.fig.add_scatter3d(
                    x=[tasks[i].pick_point.x], 
                    y=[tasks[i].pick_point.y], 
                    z=[tasks[i].pick_point.z], 
                    mode='markers+text',
                    marker=dict(color=color, size=marker_size, symbol='square'),
                    name=f"Pick {tasks[i].task_id}: {pick_str}",
                    text=[tasks[i].task_id])
                
    

    def trace_path(self, point_path, path_name="", color='rgb(31,119,180)', t_start=None, show_t=False):
        print(f"Tracing path {path_name}")
        if len(point_path) > 0:
            xs = [point.x for point in point_path]
            ys = [point.y for point in point_path]
            zs = [point.z for point in point_path]
            if t_start == None:
                labels = [f"si={i}" for i in list(range(len(point_path)))]
            else:
                idx = list(range(len(point_path)))
                ts = list(range(t_start,t_start+len(point_path)))
                labels = [f"si={i}, t={t}" for i, t in zip(idx, ts)]
            if show_t:
                ts[0] = ""
                ts[-1] = ""
                self.fig.add_scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode='lines+markers+text',
                    marker=dict(color=color, size=3),
                    name=path_name,
                    text=ts)
            else:
                self.fig.add_scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode='lines+markers',
                    marker=dict(color=color, size=3),
                    name=path_name,
                    text=labels)
        if path_name[-2:] != "-1":
            self.fig.add_scatter3d(
                x=[point_path[0].x],
                y=[point_path[0].y],
                z=[point_path[0].z],
                mode='markers+text',
                marker=dict(color=color, size=5, symbol='square'),
                name=path_name,
                showlegend=False,
                text=path_name)

    def trace_robot_paths(self, show_t=True):
        robot_list = self.fleet.get_robots_as_list()
        bot_num = 0
        for bot in robot_list:
            for i in range(len(bot.path)):
                t_start = bot.path_len(r_end=i)
                self.trace_path(bot.path[i],f"{bot.robot_id}-{i}", 
                                self.color(bot_num), t_start, show_t=show_t)
            bot_num += 1
    
    def make_blocked_areas_meshes(self, hoverinfo="skip"):
        meshes = []
        lightness = 150
        color = f'rgb({lightness},{lightness},{lightness})'
        for blocked_area in self.wh_map.blocked_areas:
            meshes.append(self.make_zone_mesh(blocked_area, hoverinfo="skip", color=color))
        return meshes
    
    def make_simple_task_scatter(self, tasks=None, color=None):
        task_traces = []
        if tasks == None:
            tasks = self.task_list.tasks
        if color == None:
            run_color_rotation = True
        for i in range(len(tasks)):
            if run_color_rotation:
                task_num = int(tasks[i].task_id[1:])
                color = color=self.color(task_num)
            marker_size = np.linspace(10,5, len(tasks))
            task_traces.append(Scatter3d(
                x=[tasks[i].pick_point.x,tasks[i].drop_point().x], 
                y=[tasks[i].pick_point.y,tasks[i].drop_point().y], 
                z=[tasks[i].pick_point.z,tasks[i].drop_point().z], 
                mode='lines+markers+text',
                marker=dict(color=color, size=marker_size[i],
                            symbol='square'),
                name=f"Task {tasks[i].task_id}",
                text=[tasks[i].task_id]))
        return task_traces        
    
    def make_robot_scatter_frame(self, frame_num):
        robot_list = self.fleet.get_robots_as_list()
        self.fig.Scatter3d(
                x=[bot.lookup_pos(frame_num).x for bot in robot_list],
                y=[bot.lookup_pos(frame_num).y for bot in robot_list],
                z=[bot.lookup_pos(frame_num).z for bot in robot_list],
                mode='markers+text',
                marker=dict(size=5),
                name=f"Robots at t={frame_num}",
                showlegend=False,
                text=[bot.robot_id for bot in robot_list])
        
    def animation(self):
        t_max = fleet.longest_path_len()
        
        # make figure
        fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }

        # fill in most of layout
        fig_dict["layout"]["xaxis"] = {"range": [30, 85], "title": "Life Expectancy"}
        fig_dict["layout"]["yaxis"] = {"title": "GDP per Capita", "type": "log"}
        fig_dict["layout"]["hovermode"] = "closest"
        fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True},
                                        "fromcurrent": True, "transition": {"duration": 300,
                                                                            "easing": "quadratic-in-out"}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Year:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }

        # make data
        data_go = self.make_robot_scatter_frame(0)
        fig_dict["data"].append(data_go)

        # make frames
        for t in range(t_max):
            frame = {"data": [], "name": str(t)}
            data_go = self.make_robot_scatter_frame(t)
            frame["data"].append(data_go)

            fig_dict["frames"].append(frame)
            slider_step = {"args": [
                [year],
                {"frame": {"duration": 300, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 300}}
            ],
                "label": year,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)


        fig_dict["layout"]["sliders"] = [sliders_dict]

        fig = go.Figure(fig_dict)

        fig.show()