;; Specification in PDDL of the Alfred domain
;; Intended to be used with Fast Downward which supports PDDL 2.2 level 1 plus the :action-costs requirement from PDDL 3.1.

(define (domain alfred)
 (:requirements
    :strips
    :typing
 )
 (:types
  agent
  location
  receptacle
  object
  rtype
  otype
  )


 (:predicates
    (atLocation ?a - agent ?l - location)                     ; true if the agent is at the location
    (receptacleAtLocation ?r - receptacle ?l - location)      ; true if the receptacle is at the location (constant)
    (objectAtLocation ?o - object ?l - location)              ; true if the object is at the location
    (openable ?r - receptacle)                                ; true if a receptacle is openable
    (opened ?r - receptacle)                                  ; true if a receptacle is opened
    (inReceptacle ?o - object ?r - receptacle)                ; object ?o is in receptacle ?r
    (isReceptacleObject ?o - object)                          ; true if the object can have things put inside it
    (inReceptacleObject ?innerObject - object ?outerObject - object)                ; object ?innerObject is inside object ?outerObject
    (isReceptacleObjectFull ?o - object)                      ; true if the receptacle object contains something
    (wasInReceptacle ?o - object ?r - receptacle)             ; object ?o was or is in receptacle ?r now or some time in the past
    (checked ?r - receptacle)                                 ; whether the receptacle has been looked inside/visited
    (examined ?l - location)                                  ; TODO
    (receptacleType ?r - receptacle ?t - rtype)               ; the type of receptacle (Cabinet vs Cabinet|01|2...)
    (canContain ?rt - rtype ?ot - otype)                      ; true if receptacle can hold object
    (objectType ?o - object ?t - otype)                       ; the type of object (Apple vs Apple|01|2...)
    (holds ?a - agent ?o - object)                            ; object ?o is held by agent ?a
    (holdsAny ?a - agent)                                     ; agent ?a holds an object
    (holdsAnyReceptacleObject ?a - agent)                        ; agent ?a holds a receptacle object
    (full ?r - receptacle)                                    ; true if the receptacle has no remaining space
    (isClean ?o - object)                                     ; true if the object has been clean in sink
    (cleanable ?o - object)                                   ; true if the object can be placed in a sink
    (isHot ?o - object)                                       ; true if the object has been heated up
    (heatable ?o - object)                                    ; true if the object can be heated up in a microwave
    (isCool ?o - object)                                      ; true if the object has been cooled
    (coolable ?o - object)                                    ; true if the object can be cooled in the fridge
    (pickupable ?o - object)                                   ; true if the object can be picked up
    (moveable ?o - object)                                      ; true if the object can be moved
    (toggleable ?o - object)                                  ; true if the object can be turned on/off
    (isOn ?o - object)                                        ; true if the object is on
    (isToggled ?o - object)                                   ; true if the object has been toggled
    (sliceable ?o - object)                                   ; true if the object can be sliced
    (isSliced ?o - object)                                    ; true if the object is sliced
 )

;; All actions are specified such that the final arguments are the ones used
;; for performing actions in Unity.

;; agent goes to receptacle
 (:action GotoLocation
    :parameters (?a - agent ?lStart - location ?lEnd - location ?r - receptacle)
    :precondition (and
                    (atLocation ?a ?lStart)
                    (receptacleAtLocation ?r ?lEnd)
                    ;(exists (?r - receptacle) (receptacleAtLocation ?r ?lEnd))
                  )
    :effect (and
                (not (atLocation ?a ?lStart))
                (atLocation ?a ?lEnd)
            )
 )

  ;; agent picks up object from a receptacle
 (:action PickupObject
    :parameters (?a - agent ?l - location ?o - object ?r - receptacle)
    :precondition
        (and
            (pickupable ?o)
            (atLocation ?a ?l)
            (receptacleAtLocation ?r ?l)
            (inReceptacle ?o ?r)
            (not (holdsAny ?a))  ; agent's hands are empty.
            (or (not (openable ?r)) (opened ?r))  ; receptacle is opened if it is openable.
        )
    :effect
        (and
            (not (inReceptacle ?o ?r))
            (holds ?a ?o)
            (holdsAny ?a)
            (not (objectAtLocation ?o ?l))
        )
 )

 ;; agent puts down an object
 (:action PutObject
    :parameters (?a - agent ?l - location ?o - object ?r - receptacle ?ot - otype ?rt - rtype)
    :precondition (and
            (holds ?a ?o)
            (atLocation ?a ?l)
            (receptacleAtLocation ?r ?l)
            (or (not (openable ?r)) (opened ?r))    ; receptacle is opened if it is openable
            (objectType ?o ?ot)
            (receptacleType ?r ?rt)
            (canContain ?rt ?ot)
            )
    :effect (and
                (inReceptacle ?o ?r)
                (objectAtLocation ?o ?l)
                ;(full ?r)
                (not (holds ?a ?o))
                (not (holdsAny ?a))
            )
 )


)
