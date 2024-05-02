#include "UltrasonicSubmodule/UltrasonicSubmodule.cpp"
#include "InfraredSubModule/InfraredSubmodule.cpp"

enum SensorState {
    Initiating = 0,
    Safe = 1,
    Close = 2,
    Warning = 3,
    Dangerous = 4,

};

class ObstacleDetectionModule{
    public:
        SensorState IRState, FrontState, BackState;
    private:
        // Sensor pins
        int _pinIR, _FrontEcho, _FrontTrig, _BackEcho, _BackTrig;
        // Front sensors
        float _FrontDistance, IRDistance;

        // Back sensors
        float _BackDistance;

        ObstacleDetectionModule(int pinIR, int FrontEcho, int FrontTrig, int BackEcho, int BackTrig){

            _pinIR = pinIR;
            _FrontEcho = FrontEcho;
            _FrontTrig = FrontTrig;
            _BackEcho = BackEcho;
            _BackTrig = BackTrig;

            IRDistance = 0.0f;
            _FrontDistance = 0.0f;
            _BackDistance = 0.0f;
            IRState = Initiating;
            FrontState = Initiating;
            BackState = Initiating;
        }

        void update(){
            IRDistance = readInfrared(_pinIR);
            _FrontDistance = UltraSonicMetrics(_FrontTrig, _FrontEcho);
            _BackDistance = UltraSonicMetrics(_BackTrig, _BackEcho);

            if(IRDistance < 10){
                IRState = Dangerous;
            }else if(IRDistance < 20){
                IRState = Warning;
            }else if(IRDistance < 30){
                IRState = Close;
            }else{
                IRState = Safe;
            }

            if(_FrontDistance < 10){
                FrontState = Dangerous;
            }else if(_FrontDistance < 20){
                FrontState = Warning;
            }else if(_FrontDistance < 30){
                FrontState = Close;
            }else{
                FrontState = Safe;
            }

            if(_BackDistance < 10){
                BackState = Dangerous;
            }else if(_BackDistance < 20){
                BackState = Warning;
            }else if(_BackDistance < 30){
                BackState = Close;
            }else{
                BackState = Safe;
            }
        }
};