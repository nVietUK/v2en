import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DataController } from './data.controller';
import { DataRepository } from './data.repository';
import { Data } from './data.entity';
import { DataService } from './data.service';

@Module({
	controllers: [DataController],
	providers: [DataService],
	imports: [TypeOrmModule.forFeature([DataRepository, Data])],
})
export class DataModule {}
