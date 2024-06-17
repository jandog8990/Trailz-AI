from datasets import Dataset
import json

# Creates MTB Trail data to be used on the main 
# search page as well as the details page
class MTBTrailCreator:
    # --------------------------------------------------
    # ----- Append to area lists if elements exist ----- 
    # --------------------------------------------------
    def append_area_lists(self, areaObj, areaNames, areaRefs): 
        if 'areaName' in areaObj:
            areaNames.append(areaObj["areaName"]) 
        if 'areaRef' in areaObj:
            areaRefs.append(areaObj["areaRef"]) 
        
        return (areaNames, areaRefs)
    
    # -------------------------------------------
    # ----- Create MTB Trail Route metadata ----- 
    # -------------------------------------------
    def create_trail_metadata(self, route):
        # TODO: Trim this down to have metadata for front page vs details page 
        newRouteObj = {}
        newRouteObj['_id'] = route['_id']
        newRouteObj['trail_url'] = route["trail_url"] 
        newRouteObj['driving_directions'] = route['driving_directions']
        newRouteObj['gpx_file'] = route['gpx_file']
        newRouteObj['route_name'] = route['route_name']
        newRouteObj['difficulty'] = route['difficulty']
        newRouteObj['trail_rating'] = route['trail_rating']
        newRouteObj['average_rating'] = route['average_rating']
        newRouteObj['num_ratings'] = route['num_ratings']
        newRouteObj['trail_stats'] = route['trail_stats']
        newRouteObj['trail_images'] = route['trail_images']
        
        return newRouteObj
    
    # ----------------------------------
    # ----- Create MTB Trail Areas ----- 
    # ----------------------------------
    def create_trail_areas(self, trailArea):
        # init the area lists 
        areaNames = [] 
        areaRefs = [] 
       
        # parse out the state from trail area 
        areaObj = json.loads(trailArea['state'][0])
        areaNames.append(areaObj["areaName"])
        areaRefs.append(areaObj["areaRef"])

        # parse out sub area from area, note that the sub-areas can have
        # multiple nested areas and sub-areas so it's best to have them all
        if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0):
            # loop through the sub areas and create array 
            areaArr = trailArea['sub_area']
            for area in areaArr:
                areaObj = json.loads(area) 
                (areaNames, areaRefs) = self.append_area_lists(areaObj, areaNames, areaRefs) 

        # parse out trail system from area
        areaObj = json.loads(trailArea['trail_system'][0]) if 'trail_system' in trailArea and (len(trailArea['trail_system']) != 0) else {} 

        return self.append_area_lists(areaObj, areaNames, areaRefs) 
    
    # ------------------------------------
    # ----- Create MTB Trail Summary ----- 
    # ------------------------------------
    def create_trail_preface(self, routeObj):

        # get the route data 
        routeName = routeObj['route_name']
        areaNames = routeObj['areaNames']
        difficulty = routeObj['difficulty']
        trailRating = routeObj['trail_rating']
        averageRating = routeObj['average_rating']
        numRatings = routeObj['num_ratings']
        
        # need to put the trail area in a sentence description to be 
        # searched by the user query
        prefix = "This mtb trail route"  
        routeLocation = ", ".join(areaNames) 
        areaSentence = prefix + " is called " + routeName + ", it's located in " + routeLocation + "." 

        # trail difficulty sentence
        difficultySentence = areaSentence + " It's rated as " + trailRating + ", with a difficulty of " + difficulty + ", " 
        
        # set the average rating from users
        preface = difficultySentence + "and has an average rider rating of " + str(averageRating) + " from " + str(numRatings) + " different riders." 

        return preface 

    # ------------------------------------
    # ----- Create MTB Trail Summary ----- 
    # ------------------------------------
    def create_trail_summary(self, routeDescs, preface):
        # get the first element and append the preface
        summary = routeDescs[0] 
        summaryArr = [summary['text']] 
        summaryArr.insert(0, preface)
        summaryText = " ".join(summaryArr)
        
        # get the first 5 sentences from the text
        delim = "." 
        summaryArr =  [s+delim for s in summaryText.split(delim) if s]
        summaryArr = summaryArr[:6] 
        summaryText = "".join(summaryArr) 
        
        return summaryText 
    
    # --------------------------------------
    # ----- Create MTB Trail Full Text ----- 
    # --------------------------------------
    def create_trail_main_text(self, routeDescs, preface):
        # create the main text from all descriptions
        textArr = [desc['text'] for desc in routeDescs] 
        textArr.insert(0, preface)
        mainText = " ".join(textArr)

        return mainText

    # ------------------------------------------
    # ----- Create MTB Trail Route Preview ----- 
    # ------------------------------------------

    # NOTE: The trail route preview should have the following:
    # 1. Route name
    # 2. Trail rating (difficulty) and average user rating
    # 3. Trail distance and elevation up/down
    # 4. Trail description (overview)
    # 5. Trail image 
    def create_mtb_routes(self, mtb_routes, mtb_descs): 
        # Create the main mtb routes objects by combining routes/descriptions
        mainMTBRoutes = [] 
        for route in mtb_routes:
            # get all descriptions for the current route
            routeId = route['_id']
            routeDescs = [desc for desc in mtb_descs
                if desc['mtb_trail_route_id'] == routeId]

            # create the new route object from route and descs 
            newRouteObj = self.create_trail_metadata(route) 
            (areaNames, areaRefs) = self.create_trail_areas(route['trail_area'])
            newRouteObj['areaNames'] = areaNames
            newRouteObj['areaRefs'] = areaRefs 

            # create the preface, summary and main text 
            preface = self.create_trail_preface(newRouteObj)
            newRouteObj['summary'] = self.create_trail_summary(routeDescs, preface)
            
            # TODO: This will be used primarily for the details page
            #newRouteObj['mainText'] = self.create_trail_main_text(routeDescs, preface)

            mainMTBRoutes.append(newRouteObj)

        return mainMTBRoutes

    # -----------------------------------------
    # ----- Create MTB Trail Route Detail ----- 
    # --------------------------- -------------

    # NOTE: The trail route preview should have the following:
    # 1. Route name
    # 2. Trail rating (difficulty) and average user rating
    # 3. Trail distance and elevation up/down
    # 4. Trail description (full description)
    # 5. Trail image 
    # 6. Trail driving directions 
    # 7. Trail gpx map file 
    #def create_route_detail(self):


