function myFunc(displayData) {
	var treeData = [
                    {
                        "name": "mtech-daas-transact-sdata-uat.transient.Main_Table",
                        "parent": "null",
                        "children": [
                        {
                            "name": "mtech-daas-transact-sdata-uat.transient.DATE_DIM_V",
                            "parent": "mtech-daas-transact-sdata-uat.transient.Main_Table",
                            "children": [
                            {
                                "name": "mtech-daas-transact-sdata-uat.transient.DATE_DIM",
                                "parent": "mtech-daas-transact-sdata-uat.transient.DATE_DIM_V"
                            },
                            {
                                "name": "mtech-daas-transact-sdata-uat.transient.DATE_DIM_IDM",
                                "parent": "mtech-daas-transact-sdata-uat.transient.DATE_DIM_V"
                            }
                            ]
                        },
                        {
                            "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_V",
                            "parent": "mtech-daas-transact-sdata-uat.transient.Main_Table",
                            "children": [
                            {
                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL",
                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_V"
                            },
                            {
                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM",
                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_V",
                                "children":  [
                                    {
                                        "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S",
                                        "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM",
                                        "children":  [
                                            {
                                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S_DL",
                                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S"
                                            },
                                            {
                                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S_DN",
                                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S"
                                            },
                                            {
                                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S_UL",
                                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S"
                                            },
                                            {
                                                "name": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S_UN",
                                                "parent": "mtech-daas-transact-sdata-uat.transient.FUTURE_DTL_IDM_S"
                                            }
                                        ]
                                    }
                                ]
                            }
                            ]
                        }
                        ]
                    }
                ];
	
	
	// ************** Generate the tree diagram	 *****************
	var margin = {top: 40, right: 120, bottom: 20, left: 210},
		width = 960 - margin.right - margin.left,
		height = 500 - margin.top - margin.bottom;
		
	var i = 0,
		duration = 750,
		root;
	
	var tree = d3.layout.tree()
		.size([height, width]);
	
	var diagonal = d3.svg.diagonal()
		.projection(function(d) { return [d.y, d.x]; });
	
	var container = d3.select("body").append("div")
				.attr("id", "container")
	var svg = container.append("svg")
		.attr("width", 2000)
		.attr("height", 1000)
		//.attr("fill","green")
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
		
	
		
	//svg.append("g")
	//    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
	root = treeData[0];
	root.x0 = height / 2;
	root.y0 = 0;
	
	update(root);
	
	d3.select(self.frameElement).style("height", "500px");

}
	function update(source) {
	
	// Compute the new tree layout.
	var nodes = tree.nodes(root).reverse(),
		links = tree.links(nodes);
	
	// Normalize for fixed-depth.
	nodes.forEach(function(d) { d.y = d.depth * 400; });
	
	// Update the nodes…
	var node = svg.selectAll("g.node")
		.data(nodes, function(d) { return d.id || (d.id = ++i); });
	
	// Enter any new nodes at the parent's previous position.
	var nodeEnter = node.enter().append("g")
		.attr("class", "node")
		.attr("transform", function(d) { return "translate(" + source.x0 + "," + source.y0 + ")"; })
		.on("click", click);
	
	nodeEnter.append("circle")
		.attr("r", 1e-6)
		.style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });
		
	nodeEnter.append("text")
	.attr("x", "0")
	.attr("y", "-25")
		//.attr("x", function(d) { return d.children || d._children ? -13 : 13; })
		//.attr("dy", ".35em")
	.attr("fill", "#0a6278")
		.attr("text-anchor", function(d) { return d.children || d._children ? "middle" : "middle"; })
		.text(function(d) { return d.name; })
		//.style("fill-opacity", 1e-6);
		
	// Transition nodes to their new position.
	var nodeUpdate = node.transition()
		.duration(duration)
		.attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
	
	nodeUpdate.select("circle")
		.attr("r", 20)
		.style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });
		
	
	nodeUpdate.select("text")
		.style("fill-opacity", 1);
	
	// Transition exiting nodes to the parent's new position.
	var nodeExit = node.exit().transition()
		.duration(duration)
		.attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
		.remove();
	
	nodeExit.select("circle")
		.attr("r", 1e-6);
	
	nodeExit.select("text")
		.style("fill-opacity", 1e-6);
	
	// Update the links…
	var link = svg.selectAll("path.link")
		.data(links, function(d) { return d.target.id; });
	
	// Enter any new links at the parent's previous position.
	link.enter().insert("path", "g")
		.attr("class", "link")
		.attr("d", function(d) {
			var o = {x: source.x0, y: source.y0};
			return diagonal({target: o, source: o});
		});
	
	// Transition links to their new position.
	link.transition()
		.duration(duration)
		.attr("d", diagonal);
	
	// Transition exiting nodes to the parent's new position.
	link.exit().transition()
		.duration(duration)
		.attr("d", function(d) {
			var o = {x: source.x, y: source.y};
			return diagonal({target: o, source: o});
		})
		.remove();
	
	// Stash the old positions for transition.
	nodes.forEach(function(d) {
		d.x0 = d.x;
		d.y0 = d.y;
	});
	}
	
	// Toggle children on click.
	function click(d) {
	if (d.children) {
		d._children = d.children;
		d.children = null;
	} else {
		d.children = d._children;
		d._children = null;
	}
	update(d);
	}
