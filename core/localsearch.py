




class LocalSearch():
    def __init__(self, searchName, layerid, layerName, expression, priority, dateEvaluated=None):
        self.searchName = searchName
        self.layerid = layerid
        self.layerName = layerName
        self.expression = expression
        self.priority = priority
        self.dateEvaluated = dateEvaluated

        self.status = 'evaluated'
        self.layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not self.layer:
            self.status = "layer_deleted"
        elif dateEvaluated is None:
            self.status = "not_evaluated"