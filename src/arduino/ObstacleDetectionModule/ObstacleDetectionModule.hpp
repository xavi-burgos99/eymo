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
        // Front sensors
        float FrontDistance, IRDistance;

        // Back sensors
        float BackDistance;

        ObstacleDetectionModule(){
            IRDistance = 0.0f;
            FrontDistance = 0.0f;
            BackDistance = 0.0f;
            IRState = Initiating;
            FrontState = Initiating;
            BackState = Initiating;
        }

        void update( const int pinIR, const int FrontEcho, const int FrontTrig, const int BackEcho, const int BackTrig){
            IRDistance = readInfrared(pinIR);
            FrontDistance = UltraSonicMetrics(FrontTrig, FrontEcho);
            BackDistance = UltraSonicMetrics(BackTrig, BackEcho);

            if(IRDistance < 10){
                IRState = Dangerous;
            }else if(IRDistance < 20){
                IRState = Warning;
            }else if(IRDistance < 30){
                IRState = Close;
            }else{
                IRState = Safe;
            }

            if(FrontDistance < 10){
                FrontState = Dangerous;
            }else if(FrontDistance < 20){
                FrontState = Warning;
            }else if(FrontDistance < 30){
                FrontState = Close;
            }else{
                FrontState = Safe;
            }

            if(BackDistance < 10){
                BackState = Dangerous;
            }else if(BackDistance < 20){
                BackState = Warning;
            }else if(BackDistance < 30){
                BackState = Close;
            }else{
                BackState = Safe;
            }
        }
};